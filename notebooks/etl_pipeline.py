import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

class ETLPipeline:
    def __init__(self, raw_data_path, processed_data_path, log_path):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.log_path = log_path
        self.transformation_log = {}
        self._setup_directories()

    def _setup_directories(self):
        dirs = [os.path.dirname(self.processed_data_path), os.path.dirname(self.log_path), 'data/raw']
        for d in dirs:
            if d:
                os.makedirs(d, exist_ok=True)

    def log_transformation(self, operation, description):
        entry_id = len(self.transformation_log) + 1
        self.transformation_log[entry_id] = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'description': description
        }

    def extract(self):
        df = pd.read_csv(self.raw_data_path)
        self.log_transformation("Extraction", f"Loaded {len(df)} rows from {self.raw_data_path}")
        return df

    def clean(self, df):
        # Null Handling
        null_count = df['category'].isnull().sum()
        df['category'] = df['category'].fillna('Missing')
        self.log_transformation("Cleaning - Nulls", f"Filled {null_count} nulls in 'category'")

        # Outlier Capping
        threshold = 140.0
        outliers = (df['value'] > threshold).sum()
        df['value'] = np.where(df['value'] > threshold, threshold, df['value'])
        self.log_transformation("Cleaning - Outliers", f"Capped {outliers} values in 'value' at {threshold}")

        # Date Formatting
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        self.log_transformation("Cleaning - Formatting", "Converted 'timestamp' to datetime objects")

        return df

    def run_pipeline(self):
        print("Pipeline started...")
        df = self.extract()
        df = self.clean(df)

        df.to_csv(self.processed_data_path, index=False)
        with open(self.log_path, 'w') as f:
            json.dump(self.transformation_log, f, indent=4)

        print(f"Pipeline completed. Processed data saved to {self.processed_data_path}")

if __name__ == '__main__':
    pipeline = ETLPipeline(
        raw_data_path='data/raw/sample_data.csv',
        processed_data_path='data/processed/cleaned_data.csv',
        log_path='logs/transformation_log.json'
    )
    pipeline.run_pipeline()
