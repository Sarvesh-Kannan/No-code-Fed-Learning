import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import json
import chardet

class DataProcessor:
    """Handle dataset preprocessing and analysis with robust parsing"""
    
    def __init__(self, file_path_or_buffer, filename=None):
        """
        Initialize DataProcessor
        Args:
            file_path_or_buffer: Either a file path (string) or BytesIO buffer
            filename: Original filename (required if using BytesIO)
        """
        self.file_path_or_buffer = file_path_or_buffer
        self.filename = filename
        self.is_buffer = hasattr(file_path_or_buffer, 'read')
        self.df = None
        self.original_df = None
        self.columns_info = {}
        self.preprocessing_steps = []
        
    def load_data(self):
        """
        Load dataset from file or buffer with robust parsing
        Handles various CSV formats, encodings, and Excel files
        """
        try:
            # Determine file extension
            if self.is_buffer:
                # Using BytesIO, get extension from filename
                if not self.filename:
                    raise ValueError("Filename required when using BytesIO")
                file_ext = self.filename.lower().split('.')[-1]
            else:
                # Using file path
                file_ext = self.file_path_or_buffer.lower().split('.')[-1]
            
            if file_ext == 'csv':
                self.df = self._load_csv_robust()
            elif file_ext in ['xlsx', 'xls']:
                # Try Excel first, if it fails, try CSV
                try:
                    self.df = self._load_excel_robust()
                except Exception as excel_error:
                    print(f"Excel loading failed, trying as CSV: {str(excel_error)}")
                    # Fallback to CSV parsing
                    self.df = self._load_csv_robust()
            else:
                raise ValueError("Unsupported file format. Please upload CSV or Excel files.")
            
            # Post-load validation and cleaning
            self.df = self._clean_loaded_data(self.df)
            self.original_df = self.df.copy()
            return self.df
            
        except Exception as e:
            raise ValueError(f"Error loading file: {str(e)}")
    
    def _load_csv_robust(self):
        """
        Robust CSV loading with multiple fallback strategies
        Handles different encodings, delimiters, and formats
        """
        file_source = self.file_path_or_buffer
        
        # If using BytesIO, try simpler strategies
        if self.is_buffer:
            file_source.seek(0)  # Reset to beginning
            try:
                # Try UTF-8 first
                df = pd.read_csv(file_source, encoding='utf-8', engine='python', on_bad_lines='skip')
                if len(df.columns) >= 2 and len(df) > 0:
                    return df
            except:
                pass
            
            # Try other encodings
            for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    file_source.seek(0)
                    df = pd.read_csv(file_source, encoding=encoding, engine='python', on_bad_lines='skip')
                    if len(df.columns) >= 2 and len(df) > 0:
                        return df
                except:
                    continue
            
            # Last resort
            file_source.seek(0)
            return pd.read_csv(file_source, engine='python', on_bad_lines='skip')
        
        # File path strategy (original robust loading)
        # Strategy 1: Try automatic encoding detection
        try:
            with open(file_source, 'rb') as f:
                result = chardet.detect(f.read(100000))  # Read first 100KB
                encoding = result['encoding']
            
            # Try detected encoding with common delimiters
            for sep in [',', ';', '\t', '|']:
                try:
                    df = pd.read_csv(
                        file_source,
                        encoding=encoding,
                        sep=sep,
                        engine='python',
                        on_bad_lines='skip',
                        skipinitialspace=True
                    )
                    
                    # Validate: should have at least 2 columns and some rows
                    if len(df.columns) >= 2 and len(df) > 0:
                        return df
                except:
                    continue
        except:
            pass
        
        # Strategy 2: Try common encodings explicitly
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        for encoding in encodings:
            for sep in [',', ';', '\t', '|']:
                try:
                    df = pd.read_csv(
                        file_source,
                        encoding=encoding,
                        sep=sep,
                        engine='python',
                        on_bad_lines='skip',
                        skipinitialspace=True
                    )
                    
                    if len(df.columns) >= 2 and len(df) > 0:
                        return df
                except:
                    continue
        
        # Strategy 3: Let pandas auto-detect
        try:
            df = pd.read_csv(
                file_source,
                encoding='utf-8',
                engine='python',
                on_bad_lines='skip',
                sep=None  # Auto-detect separator
            )
            return df
        except:
            pass
        
        # Strategy 4: Last resort - basic read
        df = pd.read_csv(file_source, engine='python', on_bad_lines='skip')
        return df
    
    def _load_excel_robust(self):
        """
        Robust Excel loading with error handling
        """
        file_source = self.file_path_or_buffer
        
        # If using BytesIO, simpler loading
        if self.is_buffer:
            file_source.seek(0)
            try:
                df = pd.read_excel(file_source, engine='openpyxl')
                return df
            except:
                file_source.seek(0)
                df = pd.read_excel(file_source)
                return df
        
        # File path strategy (original robust loading)
        # First, check if file is actually Excel by reading first few bytes
        try:
            with open(file_source, 'rb') as f:
                header = f.read(8)
                # Excel files start with specific signatures
                # .xlsx: PK (zip signature)
                # .xls: D0 CF (OLE signature)
                is_xlsx = header[:2] == b'PK'
                is_xls = header[:2] == b'\xD0\xCF'
                
                if not (is_xlsx or is_xls):
                    # Not an Excel file, likely a CSV with wrong extension
                    raise ValueError("File does not appear to be Excel format")
        except:
            pass  # If we can't check, continue anyway
        
        try:
            # Try with openpyxl engine (for .xlsx)
            if file_source.endswith('.xlsx'):
                df = pd.read_excel(file_source, engine='openpyxl')
            else:
                # Try with xlrd for .xls
                df = pd.read_excel(file_source)
            
            return df
        except Exception as e:
            # Try reading first sheet explicitly
            try:
                df = pd.read_excel(file_source, sheet_name=0)
                return df
            except:
                raise ValueError(f"Could not read Excel file: {str(e)}")
    
    def _clean_loaded_data(self, df):
        """
        Clean and standardize loaded data
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all', axis=0)  # Drop rows where all values are NaN
        df = df.dropna(how='all', axis=1)  # Drop columns where all values are NaN
        
        # Clean column names
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # Handle duplicate column names
        df = self._handle_duplicate_columns(df)
        
        # Infer better dtypes
        df = self._infer_dtypes(df)
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _clean_column_name(self, col_name):
        """Clean column name to be valid and readable"""
        if not isinstance(col_name, str):
            col_name = str(col_name)
        
        # Remove leading/trailing whitespace
        col_name = col_name.strip()
        
        # Replace problematic characters
        col_name = col_name.replace('\n', '_').replace('\r', '_').replace('\t', '_')
        
        # If empty, assign default name
        if not col_name or col_name.lower() == 'unnamed':
            col_name = 'Column'
        
        return col_name
    
    def _handle_duplicate_columns(self, df):
        """Handle duplicate column names by adding suffixes"""
        cols = pd.Series(df.columns)
        
        for dup in cols[cols.duplicated()].unique():
            indices = cols[cols == dup].index.tolist()
            for i, idx in enumerate(indices[1:], start=1):
                cols[idx] = f"{dup}_{i}"
        
        df.columns = cols
        return df
    
    def _infer_dtypes(self, df):
        """
        Infer better data types for columns
        Convert strings to numbers where possible
        """
        for col in df.columns:
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            # Try to convert to numeric
            try:
                # Remove common non-numeric characters
                if df[col].dtype == 'object':
                    # Try numeric conversion
                    converted = pd.to_numeric(df[col], errors='coerce')
                    
                    # If most values convert successfully (>80%), use numeric type
                    non_null_count = converted.notna().sum()
                    if non_null_count > 0 and non_null_count / len(df) > 0.8:
                        df[col] = converted
            except:
                pass
        
        return df
    
    def analyze_columns(self):
        """Analyze dataset columns and generate metadata"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        for column in self.df.columns:
            col_data = self.df[column]
            
            # Determine data type
            if pd.api.types.is_numeric_dtype(col_data):
                dtype = 'numeric'
                unique_count = col_data.nunique()
                
                # Check if it might be categorical despite being numeric
                if unique_count < 10 and len(self.df) > 50:
                    dtype = 'categorical_numeric'
            else:
                dtype = 'categorical'
            
            # Calculate statistics
            stats = {
                'dtype': dtype,
                'missing_count': int(col_data.isna().sum()),
                'missing_percentage': float((col_data.isna().sum() / len(self.df)) * 100),
                'unique_count': int(col_data.nunique()),
            }
            
            if dtype == 'numeric':
                stats.update({
                    'mean': float(col_data.mean()) if not col_data.isna().all() else None,
                    'std': float(col_data.std()) if not col_data.isna().all() else None,
                    'min': float(col_data.min()) if not col_data.isna().all() else None,
                    'max': float(col_data.max()) if not col_data.isna().all() else None,
                    'median': float(col_data.median()) if not col_data.isna().all() else None,
                })
            else:
                # For categorical columns
                value_counts = col_data.value_counts().head(10).to_dict()
                stats['top_values'] = {str(k): int(v) for k, v in value_counts.items()}
            
            self.columns_info[column] = stats
        
        return self.columns_info
    
    def preprocess(self, target_column=None):
        """Perform basic preprocessing"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        preprocessing_info = {
            'original_shape': self.df.shape,
            'steps': []
        }
        
        # 1. Handle missing values
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = self.df.select_dtypes(include=['object']).columns.tolist()
        
        # Remove target column from preprocessing if specified
        if target_column:
            if target_column in numeric_columns:
                numeric_columns.remove(target_column)
            if target_column in categorical_columns:
                categorical_columns.remove(target_column)
        
        # Impute numeric columns with median
        if numeric_columns:
            for col in numeric_columns:
                missing_before = self.df[col].isna().sum()
                if missing_before > 0:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                    preprocessing_info['steps'].append({
                        'step': 'impute_numeric',
                        'column': col,
                        'method': 'median',
                        'missing_filled': int(missing_before)
                    })
        
        # Impute categorical columns with mode
        if categorical_columns:
            for col in categorical_columns:
                missing_before = self.df[col].isna().sum()
                if missing_before > 0:
                    mode_value = self.df[col].mode()
                    if len(mode_value) > 0:
                        self.df[col].fillna(mode_value[0], inplace=True)
                        preprocessing_info['steps'].append({
                            'step': 'impute_categorical',
                            'column': col,
                            'method': 'mode',
                            'missing_filled': int(missing_before)
                        })
        
        # 2. Remove duplicate rows
        duplicates_before = self.df.duplicated().sum()
        if duplicates_before > 0:
            self.df.drop_duplicates(inplace=True)
            preprocessing_info['steps'].append({
                'step': 'remove_duplicates',
                'rows_removed': int(duplicates_before)
            })
        
        preprocessing_info['final_shape'] = self.df.shape
        preprocessing_info['rows_removed'] = int(preprocessing_info['original_shape'][0] - preprocessing_info['final_shape'][0])
        
        self.preprocessing_steps = preprocessing_info
        return preprocessing_info
    
    def get_feature_target_split(self, target_column):
        """Split data into features and target"""
        if target_column not in self.df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset")
        
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]
        
        return X, y
    
    def get_preprocessed_data(self):
        """Get the preprocessed dataframe"""
        return self.df
    
    def save_processed_data(self, output_path):
        """Save preprocessed data to file"""
        self.df.to_csv(output_path, index=False)
        return output_path
    
    def save_processed_data_to_buffer(self, buffer):
        """Save preprocessed data to BytesIO buffer"""
        self.df.to_csv(buffer, index=False)
        return buffer

