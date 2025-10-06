"""
Smart Pipeline Engine - Code-based intelligent pipeline generation
This replaces heavy LLM dependency with deterministic rule-based decisions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import IsolationForest

class SmartPipelineEngine:
    """
    Intelligent pipeline generation using rule-based decisions
    instead of relying entirely on LLM API calls
    """
    
    def __init__(self):
        self.profile = {}
        self.decisions = []
        
    def analyze_dataset(self, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """
        Deep analysis of dataset using code-based profiling
        Returns comprehensive metadata for decision making
        """
        analysis = {
            'shape': df.shape,
            'target_analysis': {},
            'feature_analysis': {},
            'data_quality': {},
            'recommendations': []
        }
        
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Target Analysis
        analysis['target_analysis'] = self._analyze_target(y, target_column)
        
        # Feature Analysis
        for col in X.columns:
            analysis['feature_analysis'][col] = self._analyze_feature(X[col], col, y)
        
        # Data Quality Assessment
        analysis['data_quality'] = self._assess_data_quality(df)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_target(self, y: pd.Series, target_name: str) -> Dict[str, Any]:
        """Analyze target variable in depth"""
        target_info = {
            'name': target_name,
            'dtype': str(y.dtype),
            'missing_count': int(y.isna().sum()),
            'missing_percent': float((y.isna().sum() / len(y)) * 100),
            'unique_count': int(y.nunique()),
        }
        
        # Determine if classification or regression
        if pd.api.types.is_numeric_dtype(y):
            unique_ratio = y.nunique() / len(y)
            if unique_ratio < 0.05:  # Less than 5% unique values
                target_info['suggested_task'] = 'classification'
                target_info['is_numeric_categorical'] = True
            else:
                target_info['suggested_task'] = 'regression'
                target_info['is_numeric_categorical'] = False
                
            # Statistics for numeric target
            target_info['mean'] = float(y.mean())
            target_info['std'] = float(y.std())
            target_info['min'] = float(y.min())
            target_info['max'] = float(y.max())
            target_info['skewness'] = float(y.skew())
        else:
            target_info['suggested_task'] = 'classification'
            target_info['is_categorical'] = True
        
        # Class distribution for classification
        if target_info.get('suggested_task') == 'classification':
            value_counts = y.value_counts()
            target_info['class_distribution'] = value_counts.to_dict()
            target_info['class_counts'] = {str(k): int(v) for k, v in value_counts.items()}
            
            # Imbalance ratio
            if len(value_counts) > 0:
                max_class = value_counts.max()
                min_class = value_counts.min()
                target_info['imbalance_ratio'] = float(max_class / min_class) if min_class > 0 else float('inf')
                target_info['is_imbalanced'] = target_info['imbalance_ratio'] > 3.0
            
        return target_info
    
    def _analyze_feature(self, series: pd.Series, col_name: str, target: pd.Series) -> Dict[str, Any]:
        """Analyze individual feature with advanced metrics"""
        feature_info = {
            'name': col_name,
            'dtype': str(series.dtype),
            'missing_count': int(series.isna().sum()),
            'missing_percent': float((series.isna().sum() / len(series)) * 100),
            'unique_count': int(series.nunique()),
            'cardinality_ratio': float(series.nunique() / len(series)),
        }
        
        # Determine feature type and characteristics
        if pd.api.types.is_numeric_dtype(series):
            feature_info['feature_type'] = 'numeric'
            
            # Check if it's actually categorical despite being numeric
            if feature_info['unique_count'] < 10 and len(series) > 50:
                feature_info['feature_type'] = 'categorical_numeric'
            
            # Numeric statistics
            if feature_info['feature_type'] == 'numeric':
                feature_info.update({
                    'mean': float(series.mean()) if not series.isna().all() else None,
                    'std': float(series.std()) if not series.isna().all() else None,
                    'min': float(series.min()) if not series.isna().all() else None,
                    'max': float(series.max()) if not series.isna().all() else None,
                    'median': float(series.median()) if not series.isna().all() else None,
                    'skewness': float(series.skew()) if not series.isna().all() else None,
                    'kurtosis': float(series.kurtosis()) if not series.isna().all() else None,
                })
                
                # Detect outliers using IQR method
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                outlier_mask = (series < (Q1 - 1.5 * IQR)) | (series > (Q3 + 1.5 * IQR))
                feature_info['outlier_count'] = int(outlier_mask.sum())
                feature_info['outlier_percent'] = float((outlier_mask.sum() / len(series)) * 100)
                
                # Correlation with target (if numeric)
                if pd.api.types.is_numeric_dtype(target):
                    try:
                        correlation = series.corr(target)
                        feature_info['target_correlation'] = float(correlation) if not np.isnan(correlation) else 0.0
                        feature_info['correlation_strength'] = self._interpret_correlation(abs(feature_info['target_correlation']))
                    except:
                        feature_info['target_correlation'] = 0.0
        else:
            feature_info['feature_type'] = 'categorical'
            
            # Categorical statistics
            value_counts = series.value_counts()
            feature_info['top_categories'] = value_counts.head(10).to_dict()
            feature_info['mode'] = str(series.mode()[0]) if len(series.mode()) > 0 else None
            feature_info['mode_frequency'] = int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
            feature_info['mode_percent'] = float((feature_info['mode_frequency'] / len(series)) * 100)
            
            # High cardinality check
            feature_info['is_high_cardinality'] = feature_info['unique_count'] > 50
            
        # Feature importance flags
        feature_info['is_critical'] = feature_info['missing_percent'] < 30
        feature_info['needs_attention'] = feature_info['missing_percent'] > 50
        
        return feature_info
    
    def _interpret_correlation(self, abs_corr: float) -> str:
        """Interpret correlation strength"""
        if abs_corr > 0.7:
            return 'strong'
        elif abs_corr > 0.4:
            return 'moderate'
        elif abs_corr > 0.2:
            return 'weak'
        else:
            return 'very_weak'
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        quality = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_missing': int(df.isna().sum().sum()),
            'missing_percent': float((df.isna().sum().sum() / (len(df) * len(df.columns))) * 100),
            'duplicate_rows': int(df.duplicated().sum()),
            'duplicate_percent': float((df.duplicated().sum() / len(df)) * 100),
        }
        
        # Overall quality score
        quality_score = 100.0
        if quality['missing_percent'] > 10:
            quality_score -= quality['missing_percent']
        if quality['duplicate_percent'] > 5:
            quality_score -= quality['duplicate_percent'] * 2
        
        quality['quality_score'] = max(0.0, min(100.0, quality_score))
        
        return quality
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        if analysis['data_quality']['missing_percent'] > 20:
            recommendations.append("High missing data detected. Consider imputation strategies.")
        
        if analysis['data_quality']['duplicate_percent'] > 5:
            recommendations.append("Duplicate rows detected. Removal recommended.")
        
        # Target recommendations
        target = analysis['target_analysis']
        if target.get('is_imbalanced'):
            recommendations.append(f"Target is imbalanced (ratio: {target['imbalance_ratio']:.2f}). Consider class balancing techniques.")
        
        # Feature recommendations
        high_missing_features = [
            name for name, info in analysis['feature_analysis'].items()
            if info['missing_percent'] > 50
        ]
        if high_missing_features:
            recommendations.append(f"Consider dropping features with >50% missing: {', '.join(high_missing_features[:3])}")
        
        high_cardinality_features = [
            name for name, info in analysis['feature_analysis'].items()
            if info.get('is_high_cardinality', False)
        ]
        if high_cardinality_features:
            recommendations.append(f"High cardinality features detected: {', '.join(high_cardinality_features[:3])}. Target encoding recommended.")
        
        return recommendations
    
    def generate_pipeline_with_fallbacks(self, analysis: Dict[str, Any], task_type: str, attempt: int = 1) -> Dict[str, Any]:
        """
        Generate pipeline with multiple fallback strategies
        If one approach fails, automatically try alternatives
        """
        try:
            return self.generate_pipeline(analysis, task_type)
        except Exception as e:
            print(f"Pipeline generation attempt {attempt} failed: {str(e)}")
            
            if attempt < 3:
                # Try with simplified analysis
                simplified_analysis = self._simplify_analysis(analysis)
                return self.generate_pipeline_with_fallbacks(simplified_analysis, task_type, attempt + 1)
            else:
                # Last resort: minimal safe pipeline
                return self._get_minimal_safe_pipeline(analysis, task_type)
    
    def _simplify_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify analysis to handle edge cases"""
        simplified = {
            'data_quality': analysis.get('data_quality', {}),
            'target_analysis': analysis.get('target_analysis', {}),
            'feature_analysis': {},
            'recommendations': []
        }
        
        # Keep only essential feature info
        for feature_name, feature_info in analysis.get('feature_analysis', {}).items():
            simplified['feature_analysis'][feature_name] = {
                'name': feature_name,
                'dtype': feature_info.get('dtype', 'unknown'),
                'feature_type': feature_info.get('feature_type', 'numeric'),
                'missing_percent': feature_info.get('missing_percent', 0),
                'unique_count': feature_info.get('unique_count', 0),
            }
        
        return simplified
    
    def _get_minimal_safe_pipeline(self, analysis: Dict[str, Any], task_type: str) -> Dict[str, Any]:
        """Ultra-safe minimal pipeline that works for any dataset"""
        # Categorize features simply
        numeric_features = []
        categorical_features = []
        
        for feature_name, feature_info in analysis.get('feature_analysis', {}).items():
            if feature_info.get('feature_type') == 'numeric':
                numeric_features.append(feature_name)
            else:
                categorical_features.append(feature_name)
        
        # Safe encoding: label encoding for all (always works)
        encoding_strategy = {col: 'label' for col in categorical_features}
        
        # Choose simple, reliable models
        if task_type == 'classification':
            models = [
                {
                    'name': 'Logistic Regression',
                    'type': 'LogisticRegression',
                    'hyperparameters': {'max_iter': 1000},
                    'description': 'Reliable linear classifier'
                },
                {
                    'name': 'Random Forest',
                    'type': 'RandomForestClassifier',
                    'hyperparameters': {'n_estimators': 50, 'max_depth': 10},
                    'description': 'Robust ensemble method'
                }
            ]
            metrics = ['accuracy', 'precision', 'recall', 'f1']
        else:
            models = [
                {
                    'name': 'Linear Regression',
                    'type': 'LinearRegression',
                    'hyperparameters': {},
                    'description': 'Simple linear predictor'
                },
                {
                    'name': 'Random Forest',
                    'type': 'RandomForestRegressor',
                    'hyperparameters': {'n_estimators': 50, 'max_depth': 10},
                    'description': 'Robust ensemble method'
                }
            ]
            metrics = ['mse', 'rmse', 'mae', 'r2']
        
        return {
            'preprocessing': {
                'numeric_features': numeric_features,
                'categorical_features': categorical_features,
                'drop_features': [],
                'imputation_strategy': {},
                'scaling_method': 'standardscaler',
                'encoding_strategy': encoding_strategy
            },
            'feature_engineering': {
                'polynomial_features': False,
                'feature_selection': False,
                'feature_selection_method': 'none',
                'outlier_treatment': []
            },
            'models': models,
            'validation': {
                'method': 'train_test_split',
                'test_size': 0.2,
                'cv_folds': 5,
                'stratify': task_type == 'classification'
            },
            'evaluation_metrics': metrics,
            'class_balancing': None,
            'decisions': [{
                'feature': 'FALLBACK',
                'decisions': [{
                    'rule': 'MINIMAL_SAFE_PIPELINE',
                    'reason': 'Using simplified pipeline for robustness',
                    'action': 'apply_safe_defaults'
                }]
            }]
        }
    
    def generate_pipeline(self, analysis: Dict[str, Any], task_type: str) -> Dict[str, Any]:
        """
        Generate ML pipeline using RULE-BASED decisions
        This is the core intelligence - no LLM needed here
        """
        pipeline = {
            'preprocessing': {
                'numeric_features': [],
                'categorical_features': [],
                'drop_features': [],
                'imputation_strategy': {},
                'scaling_method': 'standardscaler',
                'encoding_strategy': {}
            },
            'feature_engineering': {
                'polynomial_features': False,
                'feature_selection': False,
                'feature_selection_method': 'none',
                'outlier_treatment': []
            },
            'models': [],
            'validation': {
                'method': 'train_test_split',
                'test_size': 0.2,
                'cv_folds': 5,
                'stratify': task_type == 'classification'
            },
            'evaluation_metrics': [],
            'class_balancing': None,
            'decisions': []  # Track all decisions made
        }
        
        # Rule 1: Feature Classification
        for feature_name, feature_info in analysis['feature_analysis'].items():
            decision_log = {'feature': feature_name, 'decisions': []}
            
            # Rule 1.1: Drop features with >60% missing data
            if feature_info['missing_percent'] > 60:
                pipeline['preprocessing']['drop_features'].append(feature_name)
                decision_log['decisions'].append({
                    'rule': 'DROP_HIGH_MISSING',
                    'reason': f"Missing {feature_info['missing_percent']:.1f}% data",
                    'action': 'drop'
                })
            else:
                # Rule 1.2: Classify feature type
                if feature_info['feature_type'] in ['numeric']:
                    pipeline['preprocessing']['numeric_features'].append(feature_name)
                    
                    # Rule 1.2.1: Imputation strategy
                    if feature_info['missing_percent'] > 0:
                        # Use median for skewed data, mean for normal
                        if abs(feature_info.get('skewness', 0)) > 1:
                            pipeline['preprocessing']['imputation_strategy'][feature_name] = 'median'
                            decision_log['decisions'].append({
                                'rule': 'IMPUTE_SKEWED',
                                'reason': f"Skewness: {feature_info.get('skewness', 0):.2f}",
                                'action': 'median_imputation'
                            })
                        else:
                            pipeline['preprocessing']['imputation_strategy'][feature_name] = 'mean'
                    
                    # Rule 1.2.2: Outlier treatment
                    if feature_info.get('outlier_percent', 0) > 10:
                        pipeline['feature_engineering']['outlier_treatment'].append(feature_name)
                        decision_log['decisions'].append({
                            'rule': 'TREAT_OUTLIERS',
                            'reason': f"{feature_info['outlier_percent']:.1f}% outliers",
                            'action': 'clip_outliers'
                        })
                
                elif feature_info['feature_type'] in ['categorical', 'categorical_numeric']:
                    pipeline['preprocessing']['categorical_features'].append(feature_name)
                    
                    # Rule 1.3: Encoding strategy based on cardinality
                    if feature_info['unique_count'] < 10:
                        # Low cardinality - OneHot encoding
                        pipeline['preprocessing']['encoding_strategy'][feature_name] = 'onehot'
                        decision_log['decisions'].append({
                            'rule': 'ONEHOT_LOW_CARDINALITY',
                            'reason': f"Only {feature_info['unique_count']} unique values",
                            'action': 'onehot_encoding'
                        })
                    elif feature_info['unique_count'] < 50:
                        # Medium cardinality - Label encoding
                        pipeline['preprocessing']['encoding_strategy'][feature_name] = 'label'
                        decision_log['decisions'].append({
                            'rule': 'LABEL_MEDIUM_CARDINALITY',
                            'reason': f"{feature_info['unique_count']} unique values",
                            'action': 'label_encoding'
                        })
                    else:
                        # High cardinality - Target encoding
                        pipeline['preprocessing']['encoding_strategy'][feature_name] = 'target'
                        decision_log['decisions'].append({
                            'rule': 'TARGET_HIGH_CARDINALITY',
                            'reason': f"High cardinality: {feature_info['unique_count']} values",
                            'action': 'target_encoding'
                        })
                    
                    # Imputation for categorical
                    if feature_info['missing_percent'] > 0:
                        pipeline['preprocessing']['imputation_strategy'][feature_name] = 'mode'
            
            if decision_log['decisions']:
                pipeline['decisions'].append(decision_log)
        
        # Rule 2: Feature Selection
        if len(pipeline['preprocessing']['numeric_features']) + len(pipeline['preprocessing']['categorical_features']) > 50:
            pipeline['feature_engineering']['feature_selection'] = True
            pipeline['feature_engineering']['feature_selection_method'] = 'selectkbest'
            pipeline['decisions'].append({
                'feature': 'ALL',
                'decisions': [{
                    'rule': 'FEATURE_SELECTION_HIGH_DIM',
                    'reason': f"Too many features ({len(analysis['feature_analysis'])})",
                    'action': 'apply_feature_selection'
                }]
            })
        
        # Rule 3: Model Selection based on task and data characteristics
        target_info = analysis['target_analysis']
        n_samples = analysis['data_quality']['total_rows']
        
        if task_type == 'classification':
            pipeline['evaluation_metrics'] = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
            
            # Rule 3.1: Class imbalance handling
            if target_info.get('is_imbalanced', False):
                pipeline['class_balancing'] = 'class_weight'
                pipeline['decisions'].append({
                    'feature': 'TARGET',
                    'decisions': [{
                        'rule': 'BALANCE_CLASSES',
                        'reason': f"Imbalance ratio: {target_info['imbalance_ratio']:.2f}",
                        'action': 'use_class_weights'
                    }]
                })
            
            # Model selection based on dataset size and complexity
            if n_samples < 1000:
                # Small dataset - simpler models
                pipeline['models'] = [
                    {
                        'name': 'Logistic Regression',
                        'type': 'LogisticRegression',
                        'hyperparameters': {'max_iter': 1000, 'class_weight': 'balanced' if target_info.get('is_imbalanced') else None},
                        'description': 'Fast and interpretable for small datasets'
                    },
                    {
                        'name': 'Decision Tree',
                        'type': 'DecisionTreeClassifier',
                        'hyperparameters': {'max_depth': 10, 'class_weight': 'balanced' if target_info.get('is_imbalanced') else None},
                        'description': 'Simple and interpretable tree-based model'
                    }
                ]
            elif n_samples < 10000:
                # Medium dataset
                pipeline['models'] = [
                    {
                        'name': 'Random Forest',
                        'type': 'RandomForestClassifier',
                        'hyperparameters': {'n_estimators': 100, 'max_depth': 15, 'class_weight': 'balanced' if target_info.get('is_imbalanced') else None},
                        'description': 'Robust ensemble method for medium datasets'
                    },
                    {
                        'name': 'Gradient Boosting',
                        'type': 'GradientBoostingClassifier',
                        'hyperparameters': {'n_estimators': 100, 'max_depth': 5, 'learning_rate': 0.1},
                        'description': 'Powerful boosting algorithm'
                    },
                    {
                        'name': 'Logistic Regression',
                        'type': 'LogisticRegression',
                        'hyperparameters': {'max_iter': 1000, 'class_weight': 'balanced' if target_info.get('is_imbalanced') else None},
                        'description': 'Baseline linear model'
                    }
                ]
            else:
                # Large dataset
                pipeline['models'] = [
                    {
                        'name': 'Random Forest',
                        'type': 'RandomForestClassifier',
                        'hyperparameters': {'n_estimators': 200, 'max_depth': 20, 'n_jobs': -1},
                        'description': 'Scalable ensemble for large datasets'
                    },
                    {
                        'name': 'Gradient Boosting',
                        'type': 'GradientBoostingClassifier',
                        'hyperparameters': {'n_estimators': 150, 'max_depth': 7, 'learning_rate': 0.1},
                        'description': 'High-performance boosting'
                    }
                ]
        
        else:  # Regression
            pipeline['evaluation_metrics'] = ['mse', 'rmse', 'mae', 'r2']
            
            if n_samples < 1000:
                pipeline['models'] = [
                    {
                        'name': 'Linear Regression',
                        'type': 'LinearRegression',
                        'hyperparameters': {},
                        'description': 'Simple linear model for small datasets'
                    },
                    {
                        'name': 'Decision Tree',
                        'type': 'DecisionTreeRegressor',
                        'hyperparameters': {'max_depth': 10},
                        'description': 'Non-linear tree-based model'
                    }
                ]
            elif n_samples < 10000:
                pipeline['models'] = [
                    {
                        'name': 'Random Forest',
                        'type': 'RandomForestRegressor',
                        'hyperparameters': {'n_estimators': 100, 'max_depth': 15},
                        'description': 'Robust ensemble for regression'
                    },
                    {
                        'name': 'Gradient Boosting',
                        'type': 'GradientBoostingRegressor',
                        'hyperparameters': {'n_estimators': 100, 'max_depth': 5, 'learning_rate': 0.1},
                        'description': 'Powerful boosting for regression'
                    },
                    {
                        'name': 'Linear Regression',
                        'type': 'LinearRegression',
                        'hyperparameters': {},
                        'description': 'Baseline linear model'
                    }
                ]
            else:
                pipeline['models'] = [
                    {
                        'name': 'Random Forest',
                        'type': 'RandomForestRegressor',
                        'hyperparameters': {'n_estimators': 200, 'max_depth': 20, 'n_jobs': -1},
                        'description': 'Scalable regression ensemble'
                    },
                    {
                        'name': 'Gradient Boosting',
                        'type': 'GradientBoostingRegressor',
                        'hyperparameters': {'n_estimators': 150, 'max_depth': 7, 'learning_rate': 0.1},
                        'description': 'High-performance regression'
                    }
                ]
        
        return pipeline
    
    def generate_pipeline_explanation(self, pipeline: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of pipeline decisions
        This is CODE-BASED, not LLM-based
        """
        explanation_parts = []
        
        # Header
        explanation_parts.append("## Pipeline Generation Report\n")
        
        # Data Quality
        quality = analysis['data_quality']
        explanation_parts.append(f"**Dataset:** {quality['total_rows']} rows, {quality['total_columns']} columns")
        explanation_parts.append(f"**Data Quality Score:** {quality['quality_score']:.1f}/100\n")
        
        # Preprocessing decisions
        explanation_parts.append("### Preprocessing Decisions")
        
        if pipeline['preprocessing']['drop_features']:
            explanation_parts.append(f"- **Dropped {len(pipeline['preprocessing']['drop_features'])} features** due to excessive missing data (>60%)")
        
        explanation_parts.append(f"- **Numeric features:** {len(pipeline['preprocessing']['numeric_features'])} (scaled using StandardScaler)")
        explanation_parts.append(f"- **Categorical features:** {len(pipeline['preprocessing']['categorical_features'])} (encoded based on cardinality)")
        
        # Encoding strategy
        encoding_summary = {}
        for feat, strategy in pipeline['preprocessing']['encoding_strategy'].items():
            encoding_summary[strategy] = encoding_summary.get(strategy, 0) + 1
        
        if encoding_summary:
            explanation_parts.append("\n**Encoding Strategy:**")
            if 'onehot' in encoding_summary:
                explanation_parts.append(f"- OneHot Encoding: {encoding_summary['onehot']} low-cardinality features")
            if 'label' in encoding_summary:
                explanation_parts.append(f"- Label Encoding: {encoding_summary['label']} medium-cardinality features")
            if 'target' in encoding_summary:
                explanation_parts.append(f"- Target Encoding: {encoding_summary['target']} high-cardinality features")
        
        # Model selection
        explanation_parts.append(f"\n### Model Selection")
        explanation_parts.append(f"Selected {len(pipeline['models'])} models based on dataset characteristics:")
        for model in pipeline['models']:
            explanation_parts.append(f"- **{model['name']}**: {model['description']}")
        
        # Special considerations
        if pipeline.get('class_balancing'):
            explanation_parts.append(f"\n**Class Imbalance Handling:** Using weighted classes to handle imbalanced target")
        
        if pipeline['feature_engineering']['feature_selection']:
            explanation_parts.append(f"\n**Feature Selection:** Applied due to high dimensionality")
        
        return "\n".join(explanation_parts)

