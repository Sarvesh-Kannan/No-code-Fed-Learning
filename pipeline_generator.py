import google.generativeai as genai
import json
from config import Config
from smart_pipeline_engine import SmartPipelineEngine

class PipelineGenerator:
    """
    Hybrid Pipeline Generator - Code-based logic with minimal LLM usage
    Uses SmartPipelineEngine for decisions, Gemini only for explanations
    """
    
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Reduced config for shorter, focused responses
        self.generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,  # Reduced from 4096
        }
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",  # Faster, cheaper model
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        # Initialize smart engine for rule-based decisions
        self.smart_engine = SmartPipelineEngine()
    
    def generate_pipeline(self, columns_info, target_column, task_type, preprocessing_info, df=None):
        """
        Generate pipeline using CODE-BASED INTELLIGENCE
        NO LLM CALL HERE - purely deterministic
        """
        # Use smart engine for all decision-making
        analysis = self.smart_engine.analyze_dataset(df, target_column)
        pipeline_config = self.smart_engine.generate_pipeline(analysis, task_type)
        
        # Add preprocessing info from earlier steps
        pipeline_config['initial_preprocessing'] = preprocessing_info
        
        return pipeline_config, analysis
    
    def _get_default_pipeline(self, columns_info, target_column, task_type):
        """Fallback default pipeline"""
        numeric_features = [col for col, info in columns_info.items() 
                          if col != target_column and info['dtype'] == 'numeric']
        categorical_features = [col for col, info in columns_info.items() 
                               if col != target_column and info['dtype'] in ['categorical', 'categorical_numeric']]
        
        if task_type == 'classification':
            models = [
                {
                    "name": "Logistic Regression",
                    "type": "LogisticRegression",
                    "hyperparameters": {"max_iter": 1000},
                    "description": "Simple linear model for classification"
                },
                {
                    "name": "Random Forest",
                    "type": "RandomForestClassifier",
                    "hyperparameters": {"n_estimators": 100, "max_depth": 10},
                    "description": "Ensemble model for robust predictions"
                }
            ]
            metrics = ["accuracy", "precision", "recall", "f1"]
        else:
            models = [
                {
                    "name": "Linear Regression",
                    "type": "LinearRegression",
                    "hyperparameters": {},
                    "description": "Simple linear model for regression"
                },
                {
                    "name": "Random Forest",
                    "type": "RandomForestRegressor",
                    "hyperparameters": {"n_estimators": 100, "max_depth": 10},
                    "description": "Ensemble model for robust predictions"
                }
            ]
            metrics = ["mse", "rmse", "mae", "r2"]
        
        return {
            "preprocessing": {
                "numeric_features": numeric_features,
                "categorical_features": categorical_features,
                "scaling_method": "standardscaler",
                "encoding_method": "onehot"
            },
            "feature_engineering": {
                "polynomial_features": False,
                "feature_selection": False,
                "feature_selection_method": "none"
            },
            "models": models,
            "validation": {
                "method": "train_test_split",
                "test_size": 0.2,
                "cv_folds": 5
            },
            "evaluation_metrics": metrics
        }
    
    def generate_data_story(self, dataset_info, training_results, pipeline_config, analysis, feature_importances=None):
        """
        Generate comprehensive, easy-to-understand data storytelling
        Perfect for non-technical users with NO ML knowledge
        """
        
        # Extract key insights from code-based analysis
        quality_score = analysis.get('data_quality', {}).get('quality_score', 0)
        target_info = analysis.get('target_analysis', {})
        best_model = self._get_best_model_from_results(training_results)
        
        # Get dataset characteristics
        n_rows = dataset_info.get('columns', {}).get('total_rows', analysis.get('data_quality', {}).get('total_rows', 'N/A'))
        n_features = len(analysis.get('feature_analysis', {}))
        task_type = target_info.get('suggested_task', dataset_info.get('task_type', 'unknown'))
        target_name = target_info.get('name', dataset_info.get('target', 'unknown'))
        
        # Get feature importance for best model
        best_model_features = None
        if feature_importances and best_model['name'] in feature_importances:
            best_model_features = feature_importances[best_model['name']][:5]  # Top 5
        
        # Build detailed context for Gemini
        context = self._build_detailed_context(dataset_info, training_results, analysis, best_model, best_model_features)
        
        # Comprehensive prompt for non-technical explanation
        prompt = f"""
You are explaining machine learning results to someone with ZERO technical knowledge. They've never used ML before and need simple, clear explanations.

DATASET CONTEXT:
- Dataset size: {n_rows} rows (data points), {n_features} features (characteristics)
- What we're predicting: {target_name}
- Task type: {task_type}
- Data quality: {quality_score:.0f}/100

MODEL RESULTS:
- Best performing model: {best_model['name']}
- Main score: {best_model['primary_metric'].upper()} = {best_model['score']:.3f}

{context}

Create a comprehensive, easy-to-understand explanation with these sections:

## 🎯 What We Did
Explain in 2-3 simple sentences what the system just accomplished (without jargon).

## 📊 Your Results Explained
- What does "{best_model['name']}" mean? (1 sentence in simple terms)
- What does the score {best_model['score']:.3f} mean? Is it good or bad? (explain like talking to a 10-year-old)
- Translate this to real-world impact (e.g., "This means the model can predict {target_name} with X% accuracy")

## 💡 Most Important Features Influencing {target_name}
Based on the analysis, explain which features have the strongest influence on {target_name}. Use the feature importance data to explain:
- Which features matter most? (name them specifically)
- How do they influence the prediction? (in simple terms)
- Any surprising findings?

## ✅ What This Means for You
- Can you trust these predictions? (yes/no and why)
- What's the best use case for this model?
- Which factors should you focus on to influence {target_name}?

## ⚠️ Important to Know
- What are the limitations?
- When might the model make mistakes?
- Any cautions or warnings?

## 🚀 Next Steps & Recommendations
Practical, actionable advice based on the feature importance findings.

Use simple language, analogies, and examples. ALWAYS mention specific feature names from the dataset when explaining what influences the predictions.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error in data story: {str(e)}")
            # Fallback to enhanced code-generated story
            return self._generate_enhanced_code_story(analysis, training_results, best_model, dataset_info, best_model_features)
    
    def _build_detailed_context(self, dataset_info, training_results, analysis, best_model, feature_importance=None):
        """Build rich context for Gemini to understand the data"""
        context_parts = []
        
        # Add target information
        target_info = analysis.get('target_analysis', {})
        if target_info.get('is_imbalanced'):
            context_parts.append(f"⚠️ Target variable is imbalanced (ratio: {target_info.get('imbalance_ratio', 0):.1f}:1)")
        
        # Add feature insights
        feature_analysis = analysis.get('feature_analysis', {})
        if len(feature_analysis) > 0:
            numeric_count = sum(1 for f in feature_analysis.values() if f.get('feature_type') == 'numeric')
            categorical_count = len(feature_analysis) - numeric_count
            context_parts.append(f"Features: {numeric_count} numeric, {categorical_count} categorical")
        
        # Add feature importance if available
        if feature_importance:
            context_parts.append("\nTOP INFLUENTIAL FEATURES:")
            for feat in feature_importance:
                context_parts.append(f"- {feat['feature']}: {feat['importance']:.3f}")
        
        # Add data quality insights
        quality = analysis.get('data_quality', {})
        if quality.get('missing_percent', 0) > 10:
            context_parts.append(f"\n📊 {quality.get('missing_percent', 0):.1f}% of data had missing values (now handled)")
        
        # Add all model scores for comparison
        context_parts.append("\nALL MODEL SCORES:")
        for model_name, model_data in training_results.items():
            if 'error' not in model_data:
                metrics = model_data.get('metrics', {})
                if metrics:
                    metric_str = ", ".join([f"{k}: {v:.3f}" for k, v in list(metrics.items())[:3]])
                    context_parts.append(f"- {model_name}: {metric_str}")
        
        return "\n".join(context_parts)
    
    def _get_best_model_from_results(self, training_results):
        """Extract best model from training results"""
        best = {'name': 'Unknown', 'score': 0.0, 'primary_metric': 'accuracy'}
        
        for model_name, model_data in training_results.items():
            if 'error' in model_data:
                continue
            
            metrics = model_data.get('metrics', {})
            # Get first metric as primary
            if metrics:
                metric_name = list(metrics.keys())[0]
                metric_value = metrics[metric_name]
                
                # For regression, use R2 if available (higher is better)
                if 'r2' in metrics:
                    metric_name = 'r2'
                    metric_value = metrics['r2']
                
                if metric_value > best['score']:
                    best = {
                        'name': model_name,
                        'score': metric_value,
                        'primary_metric': metric_name,
                        'all_metrics': metrics
                    }
        
        return best
    
    def _generate_enhanced_code_story(self, analysis, training_results, best_model, dataset_info, feature_importance=None):
        """Enhanced fallback: Generate comprehensive story without LLM"""
        quality_score = analysis.get('data_quality', {}).get('quality_score', 0)
        target_info = analysis.get('target_analysis', {})
        task_type = target_info.get('suggested_task', 'analysis')
        target_name = target_info.get('name', 'the target')
        
        # Interpret score based on task type
        score = best_model['score']
        metric = best_model['primary_metric']
        
        if task_type == 'classification':
            if score >= 0.9:
                performance = "Excellent! 🌟"
                trust = "You can trust these predictions with high confidence."
            elif score >= 0.8:
                performance = "Very Good! ✅"
                trust = "The model performs well and can be relied upon."
            elif score >= 0.7:
                performance = "Good"
                trust = "The model shows decent performance."
            else:
                performance = "Fair"
                trust = "Consider collecting more data or trying different features."
            
            real_world = f"The model is correct about {score*100:.0f}% of the time."
        else:  # regression
            if score >= 0.8:
                performance = "Excellent! 🌟"
                trust = "The model explains most of the variation in the data."
            elif score >= 0.6:
                performance = "Good ✅"
                trust = "The model captures important patterns."
            elif score >= 0.4:
                performance = "Fair"
                trust = "The model finds some patterns but has room for improvement."
            else:
                performance = "Needs Improvement"
                trust = "Consider adding more relevant features."
            
            real_world = f"The model explains {score*100:.0f}% of the variation in {target_name}."
        
        # Build feature importance section
        feature_section = ""
        if feature_importance:
            feature_section = f"""
## 💡 Most Important Features Influencing {target_name}
Based on the analysis, here are the key factors that influence {target_name}:

"""
            for i, feat in enumerate(feature_importance, 1):
                importance_pct = feat['importance'] * 100
                feature_section += f"{i}. **{feat['feature']}** - Influence Score: {importance_pct:.1f}%\n"
            
            feature_section += f"""
These features have the strongest impact on predicting {target_name}. Focus on these factors if you want to influence the outcome.
"""
        else:
            feature_section = f"""
## 💡 Key Insights
The model analyzed all available features to find patterns that help predict {target_name}.
"""
        
        story = f"""## 🎯 What We Did
We analyzed your dataset with {analysis.get('data_quality', {}).get('total_rows', 'N/A')} rows and trained multiple machine learning models to predict **{target_name}**.

## 📊 Your Results Explained
**Best Model:** {best_model['name']}
- **Performance:** {performance}
- **Score:** {metric.upper()} = {score:.3f}
- **In Simple Terms:** {real_world}

{feature_section}

## ✅ What This Means for You
**Can you trust these predictions?** {trust}

**Data Quality:** Your data quality score is {quality_score:.0f}/100.
{self._interpret_quality_score(quality_score)}

## ✅ Model Comparison
We trained and compared multiple models:
{self._format_model_comparison(training_results)}

The **{best_model['name']}** performed best for your data.

## 🚀 Next Steps
1. **Use the Model:** You can now use this model to make predictions on new data
2. **Monitor Performance:** Test it with real cases to ensure it works as expected
3. **Improve:** Consider collecting more data if you want even better predictions

## ⚠️ Important Notes
- The model learned patterns from your {analysis.get('data_quality', {}).get('total_rows', 'N/A')} data points
- It works best with similar data to what it was trained on
- Always validate predictions with domain knowledge

---
*This is an automated analysis. The system chose the best approach based on your data characteristics.*
"""
        return story
    
    def _interpret_quality_score(self, score):
        """Interpret data quality score in simple terms"""
        if score >= 90:
            return "Excellent! Your data is clean and well-prepared."
        elif score >= 75:
            return "Good! Your data quality is solid."
        elif score >= 60:
            return "Fair. Some data quality issues were handled automatically."
        else:
            return "Your data had some issues, but we cleaned it up for you."
    
    def _format_model_comparison(self, training_results):
        """Format model comparison for non-technical users"""
        lines = []
        for model_name, model_data in training_results.items():
            if 'error' not in model_data:
                metrics = model_data.get('metrics', {})
                if metrics:
                    first_metric = list(metrics.items())[0]
                    lines.append(f"- {model_name}: {first_metric[0]} = {first_metric[1]:.3f}")
            else:
                lines.append(f"- {model_name}: (training failed)")
        return "\n".join(lines) if lines else "Multiple models were tested."
    
    def _generate_code_based_story(self, analysis, training_results, best_model):
        """Legacy fallback: Generate story without LLM"""
        quality_score = analysis.get('data_quality', {}).get('quality_score', 0)
        target_info = analysis.get('target_analysis', {})
        
        story = f"""## Model Training Results

**Dataset Quality:** {quality_score:.1f}/100

**Best Performing Model:** {best_model['name']}
- {best_model['primary_metric'].upper()}: {best_model['score']:.3f}

**Key Findings:**
- Target variable '{target_info.get('name', 'target')}' analyzed for {target_info.get('suggested_task', 'prediction')} task
- Dataset contains {analysis.get('data_quality', {}).get('total_rows', 'N/A')} samples
- {len(analysis.get('feature_analysis', {}))} features processed

**Recommendation:** The {best_model['name']} model shows strong performance. Consider deploying this model for predictions.
"""
        return story
    
    def interpret_results(self, model_name, metrics, task_type):
        """
        Generate comprehensive, easy-to-understand interpretation
        Perfect for non-technical users
        """
        
        # Code-based interpretation first
        interpretation = self._code_based_interpretation(model_name, metrics, task_type)
        
        # Enhanced LLM call for comprehensive explanation
        try:
            metrics_str = "\n".join([f"- {k}: {v:.3f}" for k, v in metrics.items() if k != 'confusion_matrix'])
            
            prompt = f"""Explain these machine learning results to someone with NO technical background:

Model: {model_name}
Task: {task_type}
Metrics:
{metrics_str}

Provide a clear, friendly explanation covering:
1. What does "{model_name}" mean in simple terms? (1 sentence)
2. What do these scores tell us? (explain each metric in everyday language)
3. Is this good performance? How confident can we be? (be specific and honest)
4. Real-world analogy to help understand (e.g., "like getting 85/100 on a test")
5. When might this model make mistakes?
6. One practical tip for using these predictions

Use simple language, no jargon. Explain like talking to a friend who has never heard of machine learning.
"""
            
            response = self.model.generate_content(prompt)
            return f"{interpretation}\n\n## 🤖 AI-Powered Deep Dive\n\n{response.text}"
        except Exception as e:
            print(f"Gemini API error in interpret_results: {str(e)}")
            return interpretation
    
    def _code_based_interpretation(self, model_name, metrics, task_type):
        """Generate interpretation using code logic"""
        lines = [f"### {model_name} Performance\n"]
        
        if task_type == 'classification':
            accuracy = metrics.get('accuracy', 0)
            
            # Performance rating
            if accuracy >= 0.9:
                rating = "Excellent"
            elif accuracy >= 0.8:
                rating = "Good"
            elif accuracy >= 0.7:
                rating = "Fair"
            else:
                rating = "Needs Improvement"
            
            lines.append(f"**Overall Rating:** {rating}")
            lines.append(f"**Accuracy:** {accuracy:.1%} - The model correctly predicts {accuracy:.1%} of cases")
            
            if 'precision' in metrics:
                lines.append(f"**Precision:** {metrics['precision']:.1%} - Of all positive predictions, {metrics['precision']:.1%} were correct")
            
            if 'recall' in metrics:
                lines.append(f"**Recall:** {metrics['recall']:.1%} - The model found {metrics['recall']:.1%} of all actual positive cases")
        
        else:  # Regression
            r2 = metrics.get('r2', 0)
            
            if r2 >= 0.8:
                rating = "Excellent"
            elif r2 >= 0.6:
                rating = "Good"
            elif r2 >= 0.4:
                rating = "Fair"
            else:
                rating = "Needs Improvement"
            
            lines.append(f"**Overall Rating:** {rating}")
            lines.append(f"**R² Score:** {r2:.3f} - The model explains {r2:.1%} of the variance in the target")
            
            if 'rmse' in metrics:
                lines.append(f"**RMSE:** {metrics['rmse']:.3f} - Average prediction error")
        
        return "\n".join(lines)

