"""
Training Pipeline Module

This module provides utilities for collecting training data and training
the ML spam classifier. It handles the complete training workflow including
data collection, preprocessing, model training, and evaluation.

Training Process:
1. Collect labeled emails from database
2. Extract text (subject + body)
3. Train/test split (80/20)
4. Train ML model (TF-IDF + Naive Bayes)
5. Evaluate performance
6. Save trained model
"""

import logging
from typing import List, Tuple, Dict, Optional
from .spam_classifier import SpamEmailClassifier
from .database import EmailDatabase
from config.settings import settings

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """
    Machine learning model training pipeline.

    Handles the complete workflow for collecting training data, training
    the spam classifier, and evaluating its performance.

    Workflow:
    1. Query database for labeled emails
    2. Extract features (text) from emails
    3. Validate data quality
    4. Train ML classifier
    5. Evaluate on test set
    6. Report metrics

    Attributes:
        classifier: SpamEmailClassifier instance
        database: EmailDatabase instance for accessing labeled emails
        min_samples: Minimum training samples required
    """

    def __init__(self, min_samples: int = None):
        """
        Initialize training pipeline.

        Args:
            min_samples: Minimum training samples required.
                Defaults to settings.MIN_TRAINING_SAMPLES (default: 50)
        """
        try:
            self.classifier = SpamEmailClassifier()
            self.database = EmailDatabase()
            self.min_samples = min_samples or getattr(settings, 'MIN_TRAINING_SAMPLES', 50)

            logger.info(f"Training Pipeline initialized (min_samples: {self.min_samples})")

        except Exception as e:
            logger.error(f"Error initializing TrainingPipeline: {e}")
            raise

    def collect_training_data(self, labeled_only: bool = True) -> Tuple[List[str], List[int], Dict]:
        """
        Collect labeled emails from database for training.

        Retrieves emails that have been labeled as safe (0) or spam (1).
        The labels typically come from:
        - Auto-classification results (from rule-based system)
        - User manual corrections (if feedback system exists)

        Args:
            labeled_only: If True, only collect emails with labels.
                         If False, include auto-labeled emails.

        Returns:
            Tuple of:
            - texts: List of email text (subject + body)
            - labels: List of labels (0=safe, 1=spam)
            - metadata: Dictionary with collection statistics

        Example:
            >>> pipeline = TrainingPipeline()
            >>> texts, labels, metadata = pipeline.collect_training_data()
            >>> print(f"Collected {metadata['total_emails']} emails")
            Collected 127 emails
        """
        try:
            logger.info("Collecting training data from database...")

            # Get labeled emails from database
            emails = self.database.get_labeled_emails(labeled_only=labeled_only)

            logger.info(f"Retrieved {len(emails)} labeled emails")

            # Extract text and labels
            texts = []
            labels = []
            label_counts = {'safe': 0, 'spam': 0}

            for email in emails:
                try:
                    # Combine subject and body
                    subject = email.get('subject', '').strip()
                    body = email.get('body', '').strip()
                    text = f"{subject} {body}".strip()

                    # Skip empty emails
                    if not text or len(text) < 5:
                        logger.debug(f"Skipping empty email: {email.get('id')}")
                        continue

                    # Get label
                    label = email.get('label', 0)
                    if label not in [0, 1]:
                        logger.warning(f"Invalid label {label}, skipping email")
                        continue

                    texts.append(text)
                    labels.append(label)

                    # Count labels
                    if label == 0:
                        label_counts['safe'] += 1
                    else:
                        label_counts['spam'] += 1

                except Exception as e:
                    logger.debug(f"Error processing email: {e}")
                    continue

            # Generate metadata
            metadata = {
                'total_emails': len(texts),
                'safe_emails': label_counts['safe'],
                'spam_emails': label_counts['spam'],
                'safe_percentage': label_counts['safe'] / len(texts) * 100 if texts else 0,
                'spam_percentage': label_counts['spam'] / len(texts) * 100 if texts else 0,
                'source': 'database',
            }

            logger.info(
                f"Collected training data: {metadata['total_emails']} emails "
                f"({label_counts['safe']} safe, {label_counts['spam']} spam)"
            )

            return texts, labels, metadata

        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            raise

    def validate_training_data(self, texts: List[str], labels: List[int]) -> Dict:
        """
        Validate training data quality.

        Checks:
        - Sufficient number of samples
        - Balanced classes
        - Text quality

        Args:
            texts: List of training texts
            labels: List of labels

        Returns:
            Dictionary with validation results

        Example:
            >>> validation = pipeline.validate_training_data(texts, labels)
            >>> if not validation['is_valid']:
            ...     print(validation['issues'])
        """
        issues = []
        warnings = []

        # Check sample count
        if len(texts) < self.min_samples:
            issues.append(
                f"Insufficient samples: {len(texts)} < {self.min_samples} required"
            )

        # Check class balance
        if len(texts) > 0:
            spam_count = sum(labels)
            safe_count = len(labels) - spam_count

            if spam_count == 0 or safe_count == 0:
                issues.append("No positive or negative samples")

            # Warn if heavily imbalanced
            if spam_count > 0 and safe_count > 0:
                ratio = spam_count / safe_count if spam_count > safe_count else safe_count / spam_count
                if ratio > 3:  # More than 3:1 ratio
                    warnings.append(f"Imbalanced classes (ratio: {ratio:.1f}:1)")

        # Check text quality
        avg_text_length = sum(len(t) for t in texts) / len(texts) if texts else 0
        if avg_text_length < 10:
            warnings.append("Average text length is very short")

        is_valid = len(issues) == 0

        return {
            'is_valid': is_valid,
            'total_samples': len(texts),
            'issues': issues,
            'warnings': warnings,
        }

    def train_model(self, texts: List[str], labels: List[int]) -> Dict:
        """
        Train ML classifier on provided data.

        Args:
            texts: List of training texts
            labels: List of labels (0=safe, 1=spam)

        Returns:
            Dictionary with training result

        Example:
            >>> result = pipeline.train_model(texts, labels)
            >>> print(result['status'])
            'success'
        """
        try:
            logger.info(f"Training ML classifier on {len(texts)} samples...")

            # Train classifier
            self.classifier.train(texts, labels)

            logger.info("ML classifier training complete")

            return {
                'status': 'success',
                'samples_trained': len(texts),
                'model_saved': True,
            }

        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                'status': 'error',
                'error': str(e),
            }

    def evaluate_model(self, texts: List[str], labels: List[int]) -> Dict:
        """
        Evaluate trained ML classifier.

        Args:
            texts: List of test texts
            labels: List of test labels

        Returns:
            Dictionary with evaluation metrics

        Example:
            >>> metrics = pipeline.evaluate_model(test_texts, test_labels)
            >>> print(f"Accuracy: {metrics['accuracy']:.2%}")
            Accuracy: 94.23%
        """
        try:
            logger.info(f"Evaluating model on {len(texts)} samples...")

            metrics = self.classifier.evaluate(texts, labels)

            # Log results
            if 'accuracy' in metrics:
                logger.info(
                    f"Evaluation complete - Accuracy: {metrics['accuracy']:.2%}, "
                    f"Precision: {metrics['precision']:.2%}, "
                    f"Recall: {metrics['recall']:.2%}, "
                    f"F1-Score: {metrics['f1_score']:.2%}"
                )

            return metrics

        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {'error': str(e)}

    def run_full_training(self) -> Dict:
        """
        Run complete training pipeline end-to-end.

        This is the main entry point for training. It:
        1. Collects training data from database
        2. Validates data quality
        3. Trains ML classifier
        4. Evaluates performance
        5. Reports results

        Returns:
            Dictionary with complete training results

        Example:
            >>> pipeline = TrainingPipeline()
            >>> result = pipeline.run_full_training()
            >>> if result['status'] == 'success':
            ...     print(f"Accuracy: {result['metrics']['accuracy']:.2%}")
        """
        try:
            logger.info("Starting full training pipeline...")

            # Step 1: Collect data
            logger.info("Step 1/4: Collecting training data...")
            texts, labels, metadata = self.collect_training_data()

            # Step 2: Validate data
            logger.info("Step 2/4: Validating training data...")
            validation = self.validate_training_data(texts, labels)

            if not validation['is_valid']:
                logger.error(f"Training data validation failed: {validation['issues']}")
                return {
                    'status': 'error',
                    'phase': 'validation',
                    'errors': validation['issues'],
                    'metadata': metadata,
                }

            # Log warnings
            for warning in validation['warnings']:
                logger.warning(f"Data warning: {warning}")

            # Step 3: Train model
            logger.info("Step 3/4: Training ML classifier...")
            train_result = self.train_model(texts, labels)

            if train_result['status'] != 'success':
                logger.error(f"Training failed: {train_result.get('error')}")
                return train_result

            # Step 4: Evaluate model
            logger.info("Step 4/4: Evaluating trained model...")
            metrics = self.evaluate_model(texts, labels)

            if 'error' in metrics:
                logger.warning(f"Evaluation error: {metrics['error']}")

            # Return complete results
            result = {
                'status': 'success',
                'phase': 'complete',
                'metadata': metadata,
                'validation': validation,
                'training': train_result,
                'metrics': metrics,
            }

            logger.info("Full training pipeline complete!")
            logger.info(f"Results: {result['status']}")

            return result

        except Exception as e:
            logger.error(f"Error in training pipeline: {e}")
            return {
                'status': 'error',
                'phase': 'unknown',
                'error': str(e),
            }

    def get_model_status(self) -> Dict:
        """
        Get current status of trained model.

        Returns:
            Dictionary with model information

        Example:
            >>> status = pipeline.get_model_status()
            >>> print(f"Model trained: {status['is_trained']}")
        """
        model_info = self.classifier.get_model_info()

        return {
            'is_trained': self.classifier.is_trained,
            'model_info': model_info,
            'min_samples_required': self.min_samples,
        }

    def get_feature_importance(self, top_n: int = 20) -> Dict:
        """
        Get most important features learned by model.

        Args:
            top_n: Number of top features

        Returns:
            Dictionary with feature importance

        Example:
            >>> importance = pipeline.get_feature_importance(top_n=10)
            >>> print(importance['spam_features'][:5])
        """
        return self.classifier.get_feature_importance(top_n)
