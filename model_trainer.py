import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score, classification_report, confusion_matrix
)
import joblib
import os
from datetime import datetime

class ModelTrainer:
    """Train ML models based on generated pipeline"""
    
    def __init__(self, pipeline_config, df, target_column, task_type):
        self.pipeline_config = pipeline_config
        self.df = df.copy()
        self.target_column = target_column
        self.task_type = task_type
        self.models = {}
        self.results = {}
        self.trained_models = {}
        
        # Model mappings
        self.model_classes = {
            # Classification
            'LogisticRegression': LogisticRegression,
            'RandomForestClassifier': RandomForestClassifier,
            'GradientBoostingClassifier': GradientBoostingClassifier,
            'SVC': SVC,
            'DecisionTreeClassifier': DecisionTreeClassifier,
            
            # Regression
            'LinearRegression': LinearRegression,
            'RandomForestRegressor': RandomForestRegressor,
            'GradientBoostingRegressor': GradientBoostingRegressor,
            'SVR': SVR,
            'DecisionTreeRegressor': DecisionTreeRegressor,
        }
    
    def prepare_data(self):
        """Prepare features and target"""
        # Separate features and target
        X = self.df.drop(columns=[self.target_column])
        y = self.df[self.target_column]
        
        # Handle categorical features
        categorical_features = self.pipeline_config['preprocessing']['categorical_features']
        numeric_features = self.pipeline_config['preprocessing']['numeric_features']
        
        # Get encoding strategy - support both old and new formats
        encoding_strategy = self.pipeline_config['preprocessing'].get('encoding_strategy', {})
        encoding_method = self.pipeline_config['preprocessing'].get('encoding_method', 'label')
        
        # Encode categorical features
        if categorical_features:
            # NEW FORMAT: encoding_strategy is a dictionary mapping column -> method
            if encoding_strategy and isinstance(encoding_strategy, dict):
                for col in categorical_features:
                    if col not in X.columns:
                        continue
                    
                    col_encoding = encoding_strategy.get(col, 'label')
                    
                    if col_encoding == 'onehot':
                        # OneHot encode this column
                        X = pd.get_dummies(X, columns=[col], drop_first=True, prefix=col)
                    elif col_encoding == 'target':
                        # Target encoding (simplified: use label encoding as fallback)
                        le = LabelEncoder()
                        X[col] = le.fit_transform(X[col].astype(str))
                    else:  # label encoding
                        le = LabelEncoder()
                        X[col] = le.fit_transform(X[col].astype(str))
            
            # OLD FORMAT: encoding_method is a single string for all columns
            else:
                if encoding_method == 'onehot':
                    X = pd.get_dummies(X, columns=categorical_features, drop_first=True)
                else:  # label encoding
                    for col in categorical_features:
                        if col in X.columns:
                            le = LabelEncoder()
                            X[col] = le.fit_transform(X[col].astype(str))
        
        # Encode target if classification and categorical
        self.label_encoder = None
        if self.task_type == 'classification' and y.dtype == 'object':
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(y)
        
        # Scale numeric features
        scaling_method = self.pipeline_config['preprocessing'].get('scaling_method', 'standardscaler')
        if numeric_features and scaling_method != 'none':
            numeric_cols = [col for col in numeric_features if col in X.columns]
            if numeric_cols:
                if scaling_method == 'standardscaler':
                    scaler = StandardScaler()
                else:
                    scaler = MinMaxScaler()
                
                X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
                self.scaler = scaler
        
        return X, y
    
    def train_models(self):
        """Train all models in the pipeline"""
        try:
            X, y = self.prepare_data()
        except Exception as e:
            print(f"Error preparing data: {str(e)}")
            print(f"Pipeline config keys: {self.pipeline_config.keys()}")
            print(f"Preprocessing keys: {self.pipeline_config.get('preprocessing', {}).keys()}")
            raise
        
        # Split data
        validation_config = self.pipeline_config.get('validation', {})
        test_size = validation_config.get('test_size', 0.2)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if self.task_type == 'classification' else None
        )
        
        # Store data splits for later use
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        # Train each model
        models_config = self.pipeline_config['models']
        
        for model_config in models_config:
            model_name = model_config['name']
            model_type = model_config['type']
            hyperparameters = model_config.get('hyperparameters', {})
            
            try:
                # Get model class
                if model_type not in self.model_classes:
                    print(f"Model type {model_type} not supported, skipping...")
                    continue
                
                model_class = self.model_classes[model_type]
                
                # Create and train model
                model = model_class(**hyperparameters)
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                metrics = self._calculate_metrics(y_test, y_pred)
                
                # Store results
                self.results[model_name] = {
                    'model_type': model_type,
                    'metrics': metrics,
                    'hyperparameters': hyperparameters,
                    'training_samples': len(X_train),
                    'test_samples': len(X_test)
                }
                
                self.trained_models[model_name] = model
                
                print(f"Successfully trained {model_name}")
                
            except Exception as e:
                print(f"Error training {model_name}: {str(e)}")
                self.results[model_name] = {
                    'error': str(e)
                }
        
        return self.results
    
    def _calculate_metrics(self, y_true, y_pred):
        """Calculate evaluation metrics based on task type"""
        metrics = {}
        
        if self.task_type == 'classification':
            metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
            
            # Handle binary and multiclass
            average = 'binary' if len(np.unique(y_true)) == 2 else 'weighted'
            
            metrics['precision'] = float(precision_score(y_true, y_pred, average=average, zero_division=0))
            metrics['recall'] = float(recall_score(y_true, y_pred, average=average, zero_division=0))
            metrics['f1'] = float(f1_score(y_true, y_pred, average=average, zero_division=0))
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            metrics['confusion_matrix'] = cm.tolist()
            
        else:  # regression
            metrics['mse'] = float(mean_squared_error(y_true, y_pred))
            metrics['rmse'] = float(np.sqrt(metrics['mse']))
            metrics['mae'] = float(mean_absolute_error(y_true, y_pred))
            metrics['r2'] = float(r2_score(y_true, y_pred))
        
        return metrics
    
    def save_models(self, output_dir):
        """Save trained models to disk"""
        os.makedirs(output_dir, exist_ok=True)
        
        model_paths = {}
        for model_name, model in self.trained_models.items():
            # Create safe filename
            safe_name = model_name.replace(' ', '_').lower()
            model_path = os.path.join(output_dir, f"{safe_name}.joblib")
            
            joblib.dump(model, model_path)
            model_paths[model_name] = model_path
        
        return model_paths
    
    def get_best_model(self):
        """Get the best performing model"""
        if not self.results:
            return None
        
        best_model_name = None
        best_score = -float('inf')
        
        for model_name, result in self.results.items():
            if 'error' in result:
                continue
            
            metrics = result['metrics']
            
            # Choose metric based on task type
            if self.task_type == 'classification':
                score = metrics.get('accuracy', 0)
            else:
                score = metrics.get('r2', -float('inf'))
            
            if score > best_score:
                best_score = score
                best_model_name = model_name
        
        return {
            'model_name': best_model_name,
            'model': self.trained_models.get(best_model_name),
            'results': self.results.get(best_model_name)
        }
    
    def get_feature_importance(self, model_name):
        """Get feature importance if available, normalized to sum to 1.0"""
        if model_name not in self.trained_models:
            return None
        
        model = self.trained_models[model_name]
        feature_names = self.X_train.columns.tolist()
        
        importances = None
        
        # Tree-based models have feature_importances_
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        
        # Linear models have coef_
        elif hasattr(model, 'coef_'):
            coef = model.coef_
            
            # Handle 1D and 2D arrays
            if len(coef.shape) == 1:
                importances = np.abs(coef)
            else:
                importances = np.abs(coef[0])
        
        if importances is None:
            return None
        
        # NORMALIZE: Make sure importances sum to 1.0 (so they can be expressed as percentages)
        total = np.sum(importances)
        if total > 0:
            importances = importances / total
        
        feature_importance = [
            {'feature': name, 'importance': float(imp)}
            for name, imp in zip(feature_names, importances)
        ]
        
        # Sort by importance
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return feature_importance
    
    def get_all_feature_importances(self):
        """Get feature importance for all trained models"""
        all_importances = {}
        
        for model_name in self.trained_models.keys():
            importance = self.get_feature_importance(model_name)
            if importance:
                all_importances[model_name] = importance
        
        return all_importances

