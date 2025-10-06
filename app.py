import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback

from config import Config
from database import db, User, Project, ProjectMember, Dataset, TrainingRun, ModelResult
from auth import generate_token, token_required
from data_processor import DataProcessor
from pipeline_generator import PipelineGenerator
from model_trainer import ModelTrainer
from encryption_manager import get_secure_handler

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)

# Create necessary directories
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.MODEL_FOLDER, exist_ok=True)
os.makedirs(Config.VISUALIZATION_FOLDER, exist_ok=True)

# Initialize services
pipeline_generator = PipelineGenerator()
secure_handler = get_secure_handler()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ==================== Authentication Routes ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Signup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    return jsonify({'user': current_user.to_dict()}), 200

# ==================== Project Routes ====================

@app.route('/api/projects', methods=['POST'])
@token_required
def create_project(current_user):
    """Create a new project"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'error': 'Project name is required'}), 400
        
        # Generate unique code
        code = Project.generate_unique_code()
        
        # Create project
        project = Project(
            name=name,
            code=code,
            description=description,
            creator_id=current_user.id
        )
        
        db.session.add(project)
        db.session.flush()
        
        # Add creator as owner
        member = ProjectMember(
            project_id=project.id,
            user_id=current_user.id,
            role='owner'
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create project error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/join', methods=['POST'])
@token_required
def join_project(current_user):
    """Join a project using code"""
    try:
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({'error': 'Project code is required'}), 400
        
        # Find project
        project = Project.query.filter_by(code=code).first()
        
        if not project:
            return jsonify({'error': 'Invalid project code'}), 404
        
        # Check if already a member
        existing_member = ProjectMember.query.filter_by(
            project_id=project.id,
            user_id=current_user.id
        ).first()
        
        if existing_member:
            return jsonify({'error': 'Already a member of this project'}), 400
        
        # Add as member
        member = ProjectMember(
            project_id=project.id,
            user_id=current_user.id,
            role='member'
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Joined project successfully',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Join project error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['GET'])
@token_required
def get_user_projects(current_user):
    """Get all projects for current user"""
    try:
        # Get all project memberships
        memberships = ProjectMember.query.filter_by(user_id=current_user.id).all()
        
        projects = []
        for membership in memberships:
            project = membership.project
            project_dict = project.to_dict()
            project_dict['role'] = membership.role
            projects.append(project_dict)
        
        return jsonify({'projects': projects}), 200
        
    except Exception as e:
        print(f"Get projects error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>', methods=['GET'])
@token_required
def get_project(current_user, project_id):
    """Get project details"""
    try:
        # Check membership
        membership = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        project_dict = project.to_dict()
        project_dict['role'] = membership.role
        
        # Get datasets
        datasets = Dataset.query.filter_by(project_id=project_id).all()
        project_dict['datasets'] = [d.to_dict() for d in datasets]
        
        # Get members
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        project_dict['members'] = [
            {
                'user_id': m.user_id,
                'email': m.user.email,
                'role': m.role,
                'joined_at': m.joined_at.isoformat()
            }
            for m in members
        ]
        
        return jsonify({'project': project_dict}), 200
        
    except Exception as e:
        print(f"Get project error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== Dataset Routes ====================

@app.route('/api/projects/<int:project_id>/datasets/upload', methods=['POST'])
@token_required
def upload_dataset(current_user, project_id):
    """Upload and analyze dataset"""
    try:
        # Check membership
        membership = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV and Excel files are allowed'}), 400
        
        # Read file into memory
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        # Process dataset from memory
        from io import BytesIO
        file_stream = BytesIO(file_content)
        processor = DataProcessor(file_stream, filename=filename)
        processor.load_data()
        columns_info = processor.analyze_columns()
        preprocessing_info = processor.preprocess()
        
        # Get preprocessed data as bytes
        preprocessed_buffer = BytesIO()
        processor.save_processed_data_to_buffer(preprocessed_buffer)
        preprocessed_buffer.seek(0)
        preprocessed_data = preprocessed_buffer.read()
        
        # Get project for encryption
        project = Project.query.get(project_id)
        
        # 🔒 ENCRYPT THE DATASET - Privacy-First Feature
        encrypted_data_info = secure_handler.prepare_dataset_for_storage(
            preprocessed_data,
            project.code,
            current_user.id
        )
        
        # Save to database (store ENCRYPTED file in Neon)
        dataset = Dataset(
            project_id=project_id,
            user_id=current_user.id,
            filename=filename,
            file_data=encrypted_data_info['encrypted_data'],  # 🔒 Encrypted!
            file_size=encrypted_data_info['file_size'],  # Original size
            columns_info=columns_info,
            preprocessing_info=preprocessing_info
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return jsonify({
            'message': 'Dataset uploaded and analyzed successfully',
            'dataset': dataset.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Upload dataset error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/datasets/<int:dataset_id>/configure', methods=['POST'])
@token_required
def configure_dataset(current_user, dataset_id):
    """Configure target variable and task type"""
    try:
        dataset = Dataset.query.get(dataset_id)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Check access
        membership = ProjectMember.query.filter_by(
            project_id=dataset.project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        target_variable = data.get('target_variable')
        task_type = data.get('task_type')
        
        if not target_variable or not task_type:
            return jsonify({'error': 'Target variable and task type are required'}), 400
        
        if task_type not in ['classification', 'regression']:
            return jsonify({'error': 'Invalid task type'}), 400
        
        # Update dataset
        dataset.target_variable = target_variable
        dataset.task_type = task_type
        db.session.commit()
        
        return jsonify({
            'message': 'Dataset configured successfully',
            'dataset': dataset.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Configure dataset error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/datasets/<int:dataset_id>/generate-pipeline', methods=['POST'])
@token_required
def generate_pipeline_route(current_user, dataset_id):
    """Generate ML pipeline using Smart Engine (code-based)"""
    try:
        dataset = Dataset.query.get(dataset_id)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Check access
        membership = ProjectMember.query.filter_by(
            project_id=dataset.project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        if not dataset.target_variable or not dataset.task_type:
            return jsonify({'error': 'Dataset not configured. Set target variable and task type first'}), 400
        
        # Load dataset for analysis (handle both old and new data)
        from io import BytesIO
        if dataset.file_data:
            # Get project for decryption
            project = Project.query.get(dataset.project_id)
            
            # 🔓 DECRYPT THE DATASET - Privacy-First Feature
            try:
                decrypted_data = secure_handler.retrieve_dataset_from_storage(
                    dataset.file_data,
                    project.code,
                    dataset.user_id
                )
                file_stream = BytesIO(decrypted_data)
                processor = DataProcessor(file_stream, filename=dataset.filename)
            except Exception as decrypt_error:
                print(f"Decryption failed, trying unencrypted (backward compatibility): {decrypt_error}")
                # Fallback for old unencrypted data
                file_stream = BytesIO(dataset.file_data)
                processor = DataProcessor(file_stream, filename=dataset.filename)
        else:
            # Old: Load from file path (backward compatibility)
            processor = DataProcessor(dataset.file_path)
        df = processor.load_data()
        
        # Generate pipeline using SMART ENGINE with fallbacks (no LLM needed here)
        try:
            pipeline_config, analysis = pipeline_generator.generate_pipeline(
                dataset.columns_info,
                dataset.target_variable,
                dataset.task_type,
                dataset.preprocessing_info,
                df=df
            )
        except Exception as e:
            print(f"Primary pipeline generation failed, using fallbacks: {str(e)}")
            # Use fallback mechanism
            analysis = pipeline_generator.smart_engine.analyze_dataset(df, dataset.target_variable)
            pipeline_config = pipeline_generator.smart_engine.generate_pipeline_with_fallbacks(
                analysis,
                dataset.task_type
            )
        
        # Generate human-readable explanation (code-based)
        explanation = pipeline_generator.smart_engine.generate_pipeline_explanation(
            pipeline_config,
            analysis
        )
        
        # Store analysis for later use
        pipeline_config['analysis'] = analysis
        pipeline_config['explanation'] = explanation
        
        # Create training run
        training_run = TrainingRun(
            dataset_id=dataset.id,
            pipeline=pipeline_config,
            status='pending'
        )
        
        db.session.add(training_run)
        db.session.commit()
        
        return jsonify({
            'message': 'Pipeline generated successfully using Smart Engine',
            'training_run': training_run.to_dict(),
            'explanation': explanation
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Generate pipeline error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/training-runs/<int:training_run_id>/train', methods=['POST'])
@token_required
def train_models(current_user, training_run_id):
    """Train models based on pipeline"""
    try:
        training_run = TrainingRun.query.get(training_run_id)
        
        if not training_run:
            return jsonify({'error': 'Training run not found'}), 404
        
        dataset = training_run.dataset
        
        # Check access
        membership = ProjectMember.query.filter_by(
            project_id=dataset.project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update status
        training_run.status = 'running'
        db.session.commit()
        
        # Load data (handle both old and new data)
        from io import BytesIO
        if dataset.file_data:
            # Get project for decryption
            project = Project.query.get(dataset.project_id)
            
            # 🔓 DECRYPT THE DATASET - Privacy-First Feature
            try:
                decrypted_data = secure_handler.retrieve_dataset_from_storage(
                    dataset.file_data,
                    project.code,
                    dataset.user_id
                )
                file_stream = BytesIO(decrypted_data)
                processor = DataProcessor(file_stream, filename=dataset.filename)
            except Exception as decrypt_error:
                print(f"Decryption failed, trying unencrypted (backward compatibility): {decrypt_error}")
                # Fallback for old unencrypted data
                file_stream = BytesIO(dataset.file_data)
                processor = DataProcessor(file_stream, filename=dataset.filename)
        else:
            # Old: Load from file path (backward compatibility)
            processor = DataProcessor(dataset.file_path)
        df = processor.load_data()
        
        # Train models
        trainer = ModelTrainer(
            training_run.pipeline,
            df,
            dataset.target_variable,
            dataset.task_type
        )
        
        results = trainer.train_models()
        
        # Save models
        model_dir = os.path.join(Config.MODEL_FOLDER, f"training_{training_run.id}")
        model_paths = trainer.save_models(model_dir)
        
        # Get best model
        best_model_info = trainer.get_best_model()
        
        # Get feature importances for all models
        feature_importances = trainer.get_all_feature_importances()
        
        # Update training run
        training_run.status = 'completed'
        training_run.metrics = results
        training_run.model_path = model_dir
        training_run.completed_at = datetime.utcnow()
        
        # Generate data story using MINIMAL LLM (only for natural language)
        dataset_info = {
            'columns': dataset.columns_info,
            'preprocessing': dataset.preprocessing_info,
            'target': dataset.target_variable,
            'task_type': dataset.task_type
        }
        
        # Get analysis from pipeline if available
        analysis = training_run.pipeline.get('analysis', {})
        
        # Generate story with minimal LLM usage + feature importance
        data_story = pipeline_generator.generate_data_story(
            dataset_info,
            results,
            training_run.pipeline,
            analysis,
            feature_importances
        )
        
        # Generate interpretation with code-based logic + minimal LLM
        interpretation = pipeline_generator.interpret_results(
            best_model_info['model_name'],
            best_model_info['results']['metrics'],
            dataset.task_type
        )
        
        # Create model result with feature importance
        results_with_importance = {
            'models': results,
            'feature_importances': feature_importances,
            'best_model': best_model_info['model_name']
        }
        
        model_result = ModelResult(
            training_run_id=training_run.id,
            results_json=results_with_importance,
            data_story=data_story,
            interpretation=interpretation
        )
        
        db.session.add(model_result)
        db.session.commit()
        
        return jsonify({
            'message': 'Training completed successfully',
            'training_run': training_run.to_dict(),
            'results': model_result.to_dict(),
            'feature_importances': feature_importances,
            'visualizations': {
                'feature_importance': feature_importances.get(best_model_info['model_name'], [])[:10] if feature_importances else []
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        # Update training run with error
        if training_run:
            training_run.status = 'failed'
            training_run.error_message = str(e)
            training_run.completed_at = datetime.utcnow()
            db.session.commit()
        
        print(f"Training error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/datasets/<int:dataset_id>/training-runs', methods=['GET'])
@token_required
def get_training_runs(current_user, dataset_id):
    """Get all training runs for a dataset"""
    try:
        dataset = Dataset.query.get(dataset_id)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Check access
        membership = ProjectMember.query.filter_by(
            project_id=dataset.project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        training_runs = TrainingRun.query.filter_by(dataset_id=dataset_id).order_by(TrainingRun.created_at.desc()).all()
        
        runs_data = []
        for run in training_runs:
            run_dict = run.to_dict()
            
            # Include results if available
            if run.results:
                result = run.results[0]
                run_dict['result'] = result.to_dict()
            
            runs_data.append(run_dict)
        
        return jsonify({'training_runs': runs_data}), 200
        
    except Exception as e:
        print(f"Get training runs error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>/federated-learning', methods=['GET'])
@token_required
def get_federated_learning_status(current_user, project_id):
    """Get federated learning status for project"""
    try:
        # Check membership
        membership = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all datasets in project
        datasets = Dataset.query.filter_by(project_id=project_id).all()
        
        federated_data = []
        for dataset in datasets:
            user = User.query.get(dataset.user_id)
            
            # Get latest training run
            latest_run = TrainingRun.query.filter_by(dataset_id=dataset.id).order_by(TrainingRun.created_at.desc()).first()
            
            dataset_info = {
                'dataset_id': dataset.id,
                'user_email': user.email,
                'filename': dataset.filename,
                'uploaded_at': dataset.uploaded_at.isoformat(),
                'target_variable': dataset.target_variable,
                'task_type': dataset.task_type,
                'training_status': None,
                'metrics': None
            }
            
            if latest_run:
                dataset_info['training_status'] = latest_run.status
                dataset_info['metrics'] = latest_run.metrics
            
            federated_data.append(dataset_info)
        
        return jsonify({
            'project_id': project_id,
            'total_participants': len(datasets),
            'participants': federated_data
        }), 200
        
    except Exception as e:
        print(f"Get federated learning status error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== Privacy & Encryption Status ====================

@app.route('/api/projects/<int:project_id>/encryption-status', methods=['GET'])
@token_required
def get_encryption_status(current_user, project_id):
    """Get encryption status and privacy information for a project"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check membership
        membership = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get encryption info
        encryption_info = secure_handler.encryption_manager.generate_project_encryption_info(
            project.code,
            current_user.id
        )
        
        # Count encrypted datasets
        datasets = Dataset.query.filter_by(project_id=project_id).all()
        encrypted_datasets = sum(1 for d in datasets if d.file_data is not None)
        
        return jsonify({
            'project_id': project_id,
            'project_name': project.name,
            'encryption_info': encryption_info,
            'statistics': {
                'total_datasets': len(datasets),
                'encrypted_datasets': encrypted_datasets,
                'encryption_rate': f"{(encrypted_datasets/len(datasets)*100) if datasets else 0:.1f}%"
            },
            'privacy_features': [
                'End-to-end encryption (AES-256)',
                'Unique encryption keys per user',
                'No plaintext data storage',
                'Secure key derivation (PBKDF2-SHA256)',
                'Privacy-first federated learning'
            ]
        }), 200
        
    except Exception as e:
        print(f"Get encryption status error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== Database Initialization ====================

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

