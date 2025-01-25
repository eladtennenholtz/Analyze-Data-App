import polars as pl
from werkzeug.utils import secure_filename
from flask import jsonify
from . import db
from .models import ExperimentType,ExperimentResult

class FileProcessingService:
    def __init__(self, file,experiment_type_id=None):
        self.file = file
        self.results = []
        self.experiment_type_id = experiment_type_id

    def process_file(self):
        
        # Process the file based on its extension
        if self.file.filename.endswith('.csv'):
            self.results = self._parse_zeta_csv()
            file_type = "CSV"
        elif self.file.filename.endswith('.xlsx'):
            self.results = self._parse_tns_excel()
            file_type = "EXCEL"
        else:
             return jsonify({"message": "Unsupported file type"}), 400
   
        # Store results in the database
        res = self._store_results(file_type,self.file.filename)
        return res

    def _parse_zeta_csv(self):
        
        try:    
            file_stream = bytes(self.file.read())
            df = pl.read_csv(file_stream)
            control_values = df.filter(pl.col("Sample Name") == "STD 1").select(pl.col("Zeta Potential (mV)"))
            control_avg = control_values.to_numpy().mean()
            formulations = df.filter(pl.col("Sample Name").str.starts_with("FORMULATION"))

            results = []
            for formulation_name in formulations["Sample Name"].unique():
                
                formulation_values = df.filter((pl.col("Sample Name") == formulation_name)).select(pl.col("Zeta Potential (mV)"))
                formulation_avg = formulation_values.to_numpy().mean()
                normalized_value = formulation_avg / control_avg
    
                if normalized_value > 0:
                    results.append({"formulation_id": formulation_name, "value": normalized_value})
                else:
                    return jsonify({"invalid file"}), 200
                    
            return results
        except Exception as e:
            return jsonify({"message": f"Error reading file: {str(e)}"}), 400


    def _parse_tns_excel(self):
    
        file_stream = bytes(self.file.read())
        
        try:
            df = pl.read_excel(file_stream)
          
            results = []
            for i in range(1,df.height):
                
                formulation_1_values = df.row(i)[1:4]  # Values from columns 1, 2, 3
                formulation_2_values = df.row(i)[4:7]   # Values from columns 4, 5, 6
                formulation_3_values = df.row(i)[7:10]    # Values from columns 7, 8, 9
                control_values = df.row(i)[10:12]  # Values from columns  10, 11, 12

                formulation_1_avg = sum(formulation_1_values) / len(formulation_1_values)
                formulation_2_avg = sum(formulation_2_values) / len(formulation_2_values)
                formulation_3_avg = sum(formulation_3_values) / len(formulation_3_values)
                control_avg = sum(control_values) / len(control_values)

                # Normalize by control (handling division by zero)
                normalized_1 = formulation_1_avg / control_avg if control_avg != 0 else None
                normalized_2 = formulation_2_avg / control_avg if control_avg != 0 else None
                normalized_3 = formulation_3_avg / control_avg if control_avg != 0 else None
                if normalized_1 <10  or normalized_2< 10 or normalized_3 <10:
                    return jsonify({"invalid file"}), 200
                if normalized_1 and normalized_1 > 10:
                    results.append({"formulation_id": f"Formulation_{i + 1}_1", "value": normalized_1})
                if normalized_2 and normalized_2 > 10:
                    results.append({"formulation_id": f"Formulation_{i + 1}_2", "value": normalized_2})
                if normalized_3 and normalized_3 > 10:
                    results.append({"formulation_id": f"Formulation_{i + 1}_2", "value": normalized_3})
                      

            return results
        except Exception as e:
            return jsonify({"message": f"Error reading file: {str(e)}"}), 400


        

    def _store_results(self, file_type,filename):
    # Ensure the experiment_type exists or create a new one
        experiment_type = ExperimentType.query.filter_by(name=filename).first()
        if experiment_type:

            return {"message": f"Experiment with name '{filename}' has already been processed."}
        if not experiment_type:
            experiment_type = ExperimentType(
                name=filename,
                file_type=file_type
            )
            db.session.add(experiment_type)
            db.session.commit()  
        for result in self.results:
            try:
                experiment_result = ExperimentResult(
                    formulation_id=result["formulation_id"],
                    calculated_value=result["value"],
                    experiment_type_id=experiment_type.id  
                )
                db.session.add(experiment_result)
            except Exception as e:
                print(f"Error while adding result: {str(e)}")
        
        try:
            db.session.commit()
            print("Experiment results committed successfully.")
            return {"message": "File processed successfully", "results": self.results}
        except Exception as e:
            print(f"Error during commit: {str(e)}")
            db.session.rollback()  # Rollback in case of error
