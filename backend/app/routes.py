from flask import Blueprint,request, jsonify
main_bp = Blueprint('main', __name__)
from .validation import validate_file_upload
from .service import FileProcessingService
from .models import ExperimentType,ExperimentResult

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    file_path = validate_file_upload(request)
    if isinstance(file_path, tuple):  
        return file_path

    service = FileProcessingService(file_path)
    response = service.process_file()

    return jsonify({
        'message': 'File processed successfully.',
        'details': response
    })

@main_bp.route('/results', methods=['GET'])
def show_results():
    results = ExperimentResult.query.join(ExperimentType).all()

    grouped_results = {}
    
    for result in results:
        experiment_type_name = result.experiment_type.name
        if experiment_type_name not in grouped_results:
            grouped_results[experiment_type_name] = []
        
        grouped_results[experiment_type_name].append({
            'formulation_id': result.formulation_id,
            'calculated_value': result.calculated_value,
            'file_type': result.experiment_type.file_type,
            'experiment_type_id': result.experiment_type_id
        })

    results_list = [
        {
            'experiment_type_name': experiment_type_name,
            'results': grouped_results[experiment_type_name]
        }
        for experiment_type_name in grouped_results
    ]
    
    return jsonify({'results': results_list})


