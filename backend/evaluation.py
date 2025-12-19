import logging
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class EvaluationMetrics:
    def __init__(self):
        self.results = []
    
    def calculate_recall_at_k(self, predicted: List[str], relevant: List[str], k: int = 10) -> float:
        """Calculate Recall@K metric"""
        if not relevant:
            return 0.0
        
        # Take top K predictions
        predicted_k = predicted[:k]
        
        # Count how many relevant items are in top K
        relevant_in_k = sum(1 for url in predicted_k if url in relevant)
        
        # Recall@K = relevant items in top K / total relevant items
        recall = relevant_in_k / len(relevant)
        
        return recall
    
    def calculate_mean_recall_at_k(self, evaluation_data: List[Dict], k: int = 10) -> float:
        """Calculate Mean Recall@K across all queries"""
        if not evaluation_data:
            return 0.0
        
        recalls = []
        for item in evaluation_data:
            recall = self.calculate_recall_at_k(
                item['predicted'],
                item['relevant'],
                k
            )
            recalls.append(recall)
        
        mean_recall = sum(recalls) / len(recalls)
        return mean_recall
    
    def evaluate_system(self, test_data: List[Dict], predict_func) -> Dict:
        """Evaluate the recommendation system"""
        logger.info(f"Evaluating system with {len(test_data)} test queries")
        
        evaluation_results = []
        
        for item in test_data:
            query = item['query']
            relevant_urls = item['relevant_urls']
            
            # Get predictions
            try:
                import asyncio
                predictions = asyncio.run(predict_func(query))
                predicted_urls = [p['url'] for p in predictions]
            except Exception as e:
                logger.error(f"Error predicting for query '{query}': {str(e)}")
                predicted_urls = []
            
            # Calculate metrics
            recall_at_5 = self.calculate_recall_at_k(predicted_urls, relevant_urls, k=5)
            recall_at_10 = self.calculate_recall_at_k(predicted_urls, relevant_urls, k=10)
            
            evaluation_results.append({
                'query': query,
                'relevant_count': len(relevant_urls),
                'predicted_count': len(predicted_urls),
                'recall@5': recall_at_5,
                'recall@10': recall_at_10,
                'predicted_urls': predicted_urls,
                'relevant_urls': relevant_urls
            })
        
        # Calculate overall metrics
        mean_recall_5 = sum(r['recall@5'] for r in evaluation_results) / len(evaluation_results)
        mean_recall_10 = sum(r['recall@10'] for r in evaluation_results) / len(evaluation_results)
        
        summary = {
            'mean_recall@5': round(mean_recall_5, 4),
            'mean_recall@10': round(mean_recall_10, 4),
            'total_queries': len(evaluation_results),
            'timestamp': datetime.now().isoformat(),
            'detailed_results': evaluation_results
        }
        
        logger.info(f"Evaluation complete: Mean Recall@10 = {mean_recall_10:.4f}")
        
        return summary
    
    def load_train_data(self, file_path: str) -> List[Dict]:
        """Load training/test data from Excel file"""
        try:
            df = pd.read_excel(file_path)
            
            # Group by query
            data = []
            for query in df['Query_Text'].unique():
                query_df = df[df['Query_Text'] == query]
                relevant_urls = query_df['Assessment_URL'].tolist()
                
                data.append({
                    'query': query,
                    'relevant_urls': relevant_urls
                })
            
            logger.info(f"Loaded {len(data)} queries from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading train data: {str(e)}")
            return []
    
    def export_predictions(self, predictions: List[Dict], output_path: str):
        """Export predictions to CSV format"""
        try:
            rows = []
            for pred in predictions:
                query = pred['query']
                for url in pred['predicted_urls']:
                    rows.append({
                        'Query': query,
                        'Assessment_url': url
                    })
            
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Exported predictions to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting predictions: {str(e)}")
