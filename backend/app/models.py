from .database import db
import enum 

class ExperimentType(db.Model):
    __tablename__ = 'experiment_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)

class ExperimentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    formulation_id = db.Column(db.String(50), nullable=False)
    calculated_value = db.Column(db.Float, nullable=False)
    experiment_type_id = db.Column(db.Integer, db.ForeignKey('experiment_type.id'))
    experiment_type = db.relationship('ExperimentType', backref='results')

    def __repr__(self):
        return f"<ExperimentResult {self.formulation_id}: {self.calculated_value}>"
