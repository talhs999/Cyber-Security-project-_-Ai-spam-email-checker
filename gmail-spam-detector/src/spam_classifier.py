"""
Machine Learning Spam Classifier Module

This module implements a scikit-learn based email spam classifier using
TF-IDF vectorization and Naive Bayes classification.

ML Pipeline:
1. TF-IDF Vectorization: Converts email text to numerical features
2. Naive Bayes: Learns probability patterns for spam vs legitimate emails
3. Model Persistence: Save/load trained models using joblib

This classifier learns from labeled training data and can be continuously
improved with user feedback.
"""

import logging
import os
from typing import List, Tuple, Dict, Optional
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

logger = logging.getLogger(__name__)


class SpamEmailClassifier:
    """
    Machine Learning based email spam classifier.

    Uses TF-IDF feature extraction combined with Naive Bayes classifier
    to predict if an email is spam or legitimate.

    Features:
    - Train on labeled email datasets
    - Predict spam probability for new emails
    - Evaluate model performance
    - Persist trained models to disk
    - Load pre-trained models from disk

    Attributes:
        pipeline: scikit-learn Pipeline combining TfidfVectorizer and classifier
        is_trained: Boolean indicating if model has been trained
        model_path: Path to save/load trained model
    """

    def __init__(self, model_path: str = None):
        """
        Initialize the spam classifier.

        Args:
            model_path: Path to save/load model. Defaults to 'models/spam_classifier.joblib'

        Example:
            >>> classifier = SpamEmailClassifier()
            >>> classifier.is_trained
            False
        """
        self.model_path = model_path or 'models/spam_classifier.joblib'
        self.pipeline = None
        self.is_trained = False

        # Try to load existing model
        if os.path.exists(self.model_path):
            try:
                self.load_model()
                logger.info(f"Loaded pre-trained model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")

    def create_pipeline(self) -> None:
        """
        Create a scikit-learn pipeline combining TF-IDF and Naive Bayes.

        Pipeline Steps:
        1. TfidfVectorizer: Converts text to TF-IDF features
           - max_features=5000: Keep top 5000 features
           - ngram_range=(1,2): Use unigrams and bigrams
           - min_df=2: Ignore terms appearing in < 2 documents
           - max_df=0.95: Ignore terms appearing in > 95% documents

        2. MultinomialNB: Naive Bayes classifier
           - alpha=0.1: Laplace smoothing parameter

        Returns:
            None (modifies self.pipeline)
        """
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,              # Limit features
                ngram_range=(1, 2),             # Unigrams + bigrams
                min_df=2,                       # Min document frequency
                max_df=0.95,                    # Max document frequency
                lowercase=True,                 # Lowercase all text
                stop_words='english'            # Remove English stopwords
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])

        logger.debug("ML pipeline created")

    def train(self, texts: List[str], labels: List[int]) -> None:
        """
        Train the ML classifier on labeled email data.

        Args:
            texts: List of email texts (subject + body combined)
            labels: List of labels (0=legitimate, 1=spam)

        Raises:
            ValueError: If texts and labels have different lengths
            Exception: If training fails

        Example:
            >>> classifier = SpamEmailClassifier()
            >>> texts = ["Meeting tomorrow", "Win lottery now!", "Project update"]
            >>> labels = [0, 1, 0]
            >>> classifier.train(texts, labels)
            >>> classifier.is_trained
            True
        """
        if len(texts) != len(labels):
            raise ValueError(f"Length mismatch: {len(texts)} texts vs {len(labels)} labels")

        if len(texts) < 2:
            raise ValueError("Need at least 2 training samples")

        try:
            # Create pipeline
            self.create_pipeline()

            # Train the model
            logger.info(f"Training on {len(texts)} samples...")
            self.pipeline.fit(texts, labels)
            self.is_trained = True

            # Save model
            self.save_model()

            logger.info("Model trained and saved successfully")

        except Exception as e:
            logger.error(f"Error during training: {e}")
            raise

    def predict(self, text: str) -> Tuple[int, float]:
        """
        Predict spam probability for a single email.

        Args:
            text: Email text to classify

        Returns:
            Tuple of (prediction, confidence) where:
            - prediction: 0 (legitimate) or 1 (spam)
            - confidence: Probability (0.0-1.0) of the prediction

        Example:
            >>> classifier = SpamEmailClassifier()
            >>> # ... train model first ...
            >>> prediction, confidence = classifier.predict("Win free money now!")
            >>> print(f"Spam: {prediction}, Confidence: {confidence}")
            Spam: 1, Confidence: 0.95
        """
        if not self.is_trained:
            logger.warning("Model not trained. Cannot make prediction.")
            return None, 0.0

        if not text:
            return 0, 0.0

        try:
            # Get prediction
            prediction = self.pipeline.predict([text])[0]

            # Get prediction probability
            probabilities = self.pipeline.predict_proba([text])[0]
            confidence = max(probabilities)

            return int(prediction), float(confidence)

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None, 0.0

    def predict_batch(self, texts: List[str]) -> List[Tuple[int, float]]:
        """
        Predict spam probability for multiple emails.

        Args:
            texts: List of email texts

        Returns:
            List of (prediction, confidence) tuples

        Example:
            >>> predictions = classifier.predict_batch(email_list)
            >>> for pred, conf in predictions:
            ...     print(f"Spam: {pred}, Confidence: {conf}")
        """
        results = []
        for text in texts:
            pred, conf = self.predict(text)
            results.append((pred, conf))
        return results

    def evaluate(self, texts: List[str], labels: List[int]) -> Dict:
        """
        Evaluate model performance on a dataset.

        Performs train/test split and calculates multiple metrics:
        - Accuracy: Overall correctness
        - Precision: False positive rate
        - Recall: False negative rate
        - F1-Score: Balanced metric
        - Confusion Matrix: Detailed breakdown

        Args:
            texts: List of email texts
            labels: List of labels (0=legitimate, 1=spam)

        Returns:
            Dictionary with evaluation metrics:
            {
                'accuracy': float,
                'precision': float,
                'recall': float,
                'f1_score': float,
                'confusion_matrix': array,
                'classification_report': dict,
                'model_saved': bool
            }

        Example:
            >>> metrics = classifier.evaluate(test_texts, test_labels)
            >>> print(f"Accuracy: {metrics['accuracy']:.2%}")
            Accuracy: 95.23%
        """
        if not self.is_trained and len(texts) < 10:
            return {'error': 'Not enough samples for evaluation'}

        try:
            # Split data for evaluation
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels,
                test_size=0.2,
                random_state=42,
                stratify=labels if len(set(labels)) > 1 else None
            )

            # Create and train new model on training set
            self.create_pipeline()
            self.pipeline.fit(X_train, y_train)
            self.is_trained = True

            # Predict on test set
            predictions = self.pipeline.predict(X_test)

            # Calculate metrics
            accuracy = accuracy_score(y_test, predictions)
            precision = precision_score(y_test, predictions, zero_division=0)
            recall = recall_score(y_test, predictions, zero_division=0)
            f1 = f1_score(y_test, predictions, zero_division=0)
            cm = confusion_matrix(y_test, predictions)
            report = classification_report(y_test, predictions, output_dict=True)

            metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': cm.tolist(),
                'classification_report': report,
                'test_samples': len(y_test),
                'train_samples': len(y_train),
            }

            # Save model
            self.save_model()
            metrics['model_saved'] = True

            logger.info(f"Model evaluation complete - Accuracy: {accuracy:.2%}")

            return metrics

        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return {'error': str(e)}

    def save_model(self) -> bool:
        """
        Save trained model to disk using joblib.

        Creates the models directory if it doesn't exist.

        Returns:
            True if successful, False otherwise

        Example:
            >>> classifier.save_model()
            True
        """
        if not self.pipeline:
            logger.warning("No model to save")
            return False

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            # Save model
            joblib.dump(self.pipeline, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load_model(self) -> bool:
        """
        Load trained model from disk using joblib.

        Returns:
            True if successful, False otherwise

        Example:
            >>> classifier.load_model()
            True
            >>> classifier.is_trained
            True
        """
        if not os.path.exists(self.model_path):
            logger.warning(f"Model file not found: {self.model_path}")
            return False

        try:
            self.pipeline = joblib.load(self.model_path)
            self.is_trained = True
            logger.info(f"Model loaded from {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def get_model_info(self) -> Dict:
        """
        Get information about the trained model.

        Returns:
            Dictionary with model information
        """
        if not self.is_trained:
            return {'status': 'Not trained', 'model_path': self.model_path}

        try:
            # Get number of features from vectorizer
            vectorizer = self.pipeline.named_steps['tfidf']
            n_features = len(vectorizer.get_feature_names_out())

            # Get classifier info
            classifier = self.pipeline.named_steps['classifier']

            return {
                'status': 'Trained',
                'model_path': self.model_path,
                'n_features': n_features,
                'classifier_type': classifier.__class__.__name__,
                'model_exists': os.path.exists(self.model_path),
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}

    def get_feature_importance(self, top_n: int = 20) -> Dict:
        """
        Get most important features (keywords) for spam classification.

        Args:
            top_n: Number of top features to return

        Returns:
            Dictionary with spam and legitimate top features
        """
        if not self.is_trained:
            return {'error': 'Model not trained'}

        try:
            vectorizer = self.pipeline.named_steps['tfidf']
            classifier = self.pipeline.named_steps['classifier']

            # Get feature names
            feature_names = vectorizer.get_feature_names_out()

            # Get log probabilities
            spam_class_idx = 1
            legitimate_class_idx = 0

            spam_features = classifier.feature_log_prob_[spam_class_idx]
            legitimate_features = classifier.feature_log_prob_[legitimate_class_idx]

            # Get top features for spam
            top_spam_idx = spam_features.argsort()[-top_n:][::-1]
            top_spam = [(feature_names[i], spam_features[i]) for i in top_spam_idx]

            # Get top features for legitimate
            top_legitimate_idx = legitimate_features.argsort()[-top_n:][::-1]
            top_legitimate = [(feature_names[i], legitimate_features[i]) for i in top_legitimate_idx]

            return {
                'spam_features': top_spam,
                'legitimate_features': top_legitimate,
            }
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {'error': str(e)}
