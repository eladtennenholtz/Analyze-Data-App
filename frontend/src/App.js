import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [responseMessage, setResponseMessage] = useState("");
  const [results, setResults] = useState([]);
  const [selectedExperiment, setSelectedExperiment] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const uploadFile = async () => {
    if (!file) {
      setResponseMessage("Please select a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const { message, details } = response.data;
      setResponseMessage("File processed successfully!");
      fetchResults();

    } catch (error) {
      console.error("Error uploading file:", error);
      setResponseMessage("Error uploading file.");
    }
  };

  const fetchResults = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/results");
      setResults(response.data.results || []);
    } catch (error) {
      console.error("Error fetching results:", error);
    }
  };

  const handleExperimentSelect = (experimentName) => {
    setSelectedExperiment(experimentName);
  };

  useEffect(() => {
    fetchResults();
  }, []);

  return (
    <div className="app">
      <h1 className="title">Analyze Data</h1>

      <div className="file-upload">
        <label className="file-label">
          Choose a file:
          <input type="file" onChange={handleFileChange} className="file-input" />
        </label>
        <button onClick={uploadFile} className="button primary">
          Upload File
        </button>
      </div>

      {responseMessage && <p className="response-message">{responseMessage}</p>}

      <h2 className="subtitle">Experiment Files</h2>
      <div className="experiment-buttons">
        {results.map((experiment) => (
          <button
            key={experiment.experiment_type_name}
            onClick={() => handleExperimentSelect(experiment.experiment_type_name)}
            className={`button experiment ${
              selectedExperiment === experiment.experiment_type_name ? "selected" : ""
            }`}
          >
            {experiment.experiment_type_name}
          </button>
        ))}
      </div>

      <h2 className="subtitle">Results</h2>
      {selectedExperiment ? (
        <table className="results-table">
          <thead>
            <tr>
              <th>Formulation ID</th>
              <th>Calculated Value</th>
            </tr>
          </thead>
          <tbody>
            {results
              .find((experiment) => experiment.experiment_type_name === selectedExperiment)
              ?.results.map((result, index) => (
                <tr key={index}>
                  <td>{result.formulation_id}</td>
                  <td>{result.calculated_value}</td>
                </tr>
              ))}
          </tbody>
        </table>
      ) : (
        <p className="placeholder">Select an experiment file to view its results.</p>
      )}
    </div>
  );
}

export default App;
