"""
Hybrid ML + Rule-Based Classifier Module

This module combines machine learning classification with rule-based threat detection
for improved spam and phishing email detection.

Hybrid Approach:
- ML Score (60%): Learned patterns from training data via Naive Bayes
- Threat Score (40%): Expert-crafted rules for known threat patterns
- Final Score = (ML_Score × 0.6) + (Threat_Score × 0.4)

This hybrid approach provides:
1. Accuracy of ML models for novel emails
2. Reliability of rule-based systems for known threats
3. Graceful fallback if ML model not trained
4. Backward compatibility with existing detection system
"""

import logging
from typing import Dict, List, Tuple, Optional
from .spam_classifier import SpamEmailClassifier
from .nlp_processor import NLPProcessor
from .feature_extractor import FeatureExtractor
from .threat_detector import ThreatDetector
from config.settings import settings

logger = logging.getLogger(__name__)


class HybridClassifier:
    """
    Hybrid email classifier combining ML and rule-based detection.

    The hybrid approach scores emails using both machine learning (trained on data)
    and rule-based threat detection (expert patterns), then combines them using
    weighted averaging.

    Workflow:
    1. Parse email (extract text, headers, links, attachments)
    2. Extract features (both NLP and traditional)
    3. Run ML classifier (if trained) -> ML_score (0-100)
    4. Run rule-based detector -> Threat_score (0-100)
    5. Combine scores: Final = (ML × 0.6) + (Threat × 0.4)
    6. Classify: SAFE (0-30), SUSPICIOUS (31-70), SPAM (71-100)

    Attributes:
        ml_classifier: SpamEmailClassifier instance
        nlp: NLPProcessor instance
        feature_extractor: FeatureExtractor instance
        threat_detector: ThreatDetector instance
        ml_weight: Weight for ML score in hybrid calculation
    """

    def __init__(self):
        """Initialize hybrid classifier with ML and rule-based components."""
        try:
            self.ml_classifier = SpamEmailClassifier()
            self.nlp = NLPProcessor()
            self.feature_extractor = FeatureExtractor()
            self.threat_detector = ThreatDetector()

            # Get ML weight from settings
            self.ml_weight = getattr(settings, 'ML_WEIGHT', 0.6)

            logger.info(f"Hybrid Classifier initialized (ML weight: {self.ml_weight})")

            # Log model status
            if self.ml_classifier.is_trained:
                logger.info("ML model is trained and ready")
            else:
                logger.info("ML model not trained. Using rule-based detection only.")

        except Exception as e:
            logger.error(f"Error initializing HybridClassifier: {e}")
            raise

    def classify_email(self, email_data: Dict) -> Dict:
        """
        Classify an email using hybrid ML + rule-based approach.

        Args:
            email_data: Dictionary containing email data with keys:
                - 'from': Sender email address
                - 'sender_name': Display name of sender
                - 'subject': Email subject
                - 'body': Email body text
                - 'headers': Email headers
                - 'urls': List of URLs in email
                - 'attachments': List of attachment info
                - 'has_html': Boolean if email contains HTML

        Returns:
            Dictionary with classification results:
            {
                'final_score': float (0-100),           # Final threat score
                'ml_score': float (0-100),              # ML model score
                'threat_score': float (0-100),          # Rule-based score
                'classification': str,                   # SAFE/SUSPICIOUS/SPAM
                'confidence': float (0-1),              # Confidence level
                'ml_used': bool,                        # Whether ML was used
                'ml_confidence': float (0-1),           # ML prediction confidence
                'threat_indicators': List[str],         # Detected threat patterns
                'recommendation': str,                  # Action recommendation
            }

        Example:
            >>> classifier = HybridClassifier()
            >>> result = classifier.classify_email(email_dict)
            >>> print(f"Classification: {result['classification']}")
            >>> print(f"Score: {result['final_score']}")
        """
        try:
            # Step 1: Extract features for rule-based detection
            logger.debug("Extracting features...")
            features = self.feature_extractor.extract_features(email_data)

            # Step 2: Run rule-based threat detection
            logger.debug("Running rule-based threat detection...")
            threat_result = self.threat_detector.analyze_email(email_data, features)
            threat_score = threat_result.get('overall_score', 50)
            threat_indicators = threat_result.get('indicators', [])

            # Step 3: Run ML classification (if model exists)
            ml_score = 0.0
            ml_confidence = 0.0
            ml_used = False
            ml_prediction = None

            if self.ml_classifier.is_trained:
                logger.debug("Running ML classification...")
                email_text = self._prepare_text_for_ml(email_data)

                ml_prediction, ml_confidence = self.ml_classifier.predict(email_text)

                if ml_prediction is not None:
                    # Convert ML prediction to score (0-100)
                    # 0 (safe) -> score 0-50
                    # 1 (spam) -> score 50-100
                    if ml_prediction == 1:  # Spam
                        ml_score = 50.0 + (ml_confidence * 50.0)
                    else:  # Safe/Legitimate
                        ml_score = 50.0 - (ml_confidence * 50.0)

                    ml_used = True
                    logger.debug(f"ML Score: {ml_score:.1f}, Confidence: {ml_confidence:.2%}")

            # Step 4: Combine scores using weighted average
            if ml_used:
                final_score = (ml_score * self.ml_weight) + (threat_score * (1 - self.ml_weight))
                logger.debug(
                    f"Combined score: ({ml_score:.1f} × {self.ml_weight}) + "
                    f"({threat_score:.1f} × {1-self.ml_weight}) = {final_score:.1f}"
                )
            else:
                # Fallback to rule-based if ML not trained
                final_score = threat_score
                logger.debug("ML not trained, using rule-based score only")

            # Step 5: Classify based on thresholds
            safe_threshold = getattr(settings, 'SAFE_THRESHOLD', 30)
            suspicious_threshold = getattr(settings, 'SUSPICIOUS_THRESHOLD', 70)

            if final_score < safe_threshold:
                classification = 'SAFE'
                recommendation = 'No action needed'
            elif final_score < suspicious_threshold:
                classification = 'SUSPICIOUS'
                recommendation = 'Flag for review'
            else:
                classification = 'SPAM'
                recommendation = 'Move to spam folder'

            # Step 6: Calculate overall confidence
            if ml_used:
                overall_confidence = (ml_confidence * self.ml_weight) + \
                                    ((1 - abs(threat_score - 50) / 100) * (1 - self.ml_weight))
            else:
                overall_confidence = 1.0 - abs(threat_score - 50) / 100

            result = {
                'final_score': round(final_score, 1),
                'ml_score': round(ml_score, 1) if ml_used else None,
                'threat_score': round(threat_score, 1),
                'classification': classification,
                'confidence': round(overall_confidence, 3),
                'ml_used': ml_used,
                'ml_confidence': round(ml_confidence, 3) if ml_used else None,
                'threat_indicators': threat_indicators,
                'recommendation': recommendation,
            }

            logger.info(
                f"Email classified as {classification} (Score: {final_score:.1f}, "
                f"Confidence: {overall_confidence:.2%})"
            )

            return result

        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            # Return safe default on error
            return {
                'final_score': 50.0,
                'ml_score': None,
                'threat_score': 50.0,
                'classification': 'SUSPICIOUS',
                'confidence': 0.5,
                'ml_used': False,
                'ml_confidence': None,
                'threat_indicators': ['Error during classification'],
                'recommendation': 'Manual review recommended',
                'error': str(e),
            }

    def _prepare_text_for_ml(self, email_data: Dict) -> str:
        """
        Prepare email text for ML classification.

        Combines relevant email fields (subject, body) for ML analysis.

        Args:
            email_data: Email dictionary

        Returns:
            Combined text string for ML

        Example:
            >>> text = classifier._prepare_text_for_ml(email)
            >>> print(len(text))
            1250
        """
        parts = []

        # Add subject (weighted more heavily)
        if 'subject' in email_data and email_data['subject']:
            parts.append(email_data['subject'])
            parts.append(email_data['subject'])  # Include twice for weight

        # Add body
        if 'body' in email_data and email_data['body']:
            parts.append(email_data['body'])

        # Combine and return
        text = ' '.join(parts)
        return text[:5000]  # Limit to 5000 chars for performance

    def train_from_emails(self, emails: List[Dict], labels: List[int]) -> Dict:
        """
        Train ML model from a collection of labeled emails.

        Args:
            emails: List of email dictionaries
            labels: List of labels (0=safe, 1=spam)

        Returns:
            Training result dictionary with status and metrics

        Example:
            >>> classifier = HybridClassifier()
            >>> emails = [email1, email2, email3, ...]
            >>> labels = [0, 1, 0, ...]
            >>> result = classifier.train_from_emails(emails, labels)
            >>> print(result['status'])
            'success'
        """
        try:
            logger.info(f"Preparing {len(emails)} emails for training...")

            # Extract text from emails
            texts = []
            for email in emails:
                text = self._prepare_text_for_ml(email)
                texts.append(text)

            # Train ML classifier
            logger.info("Training ML model...")
            self.ml_classifier.train(texts, labels)

            logger.info("ML model training complete")

            return {
                'status': 'success',
                'samples_trained': len(emails),
                'model_saved': True,
            }

        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'samples_trained': 0,
            }

    def evaluate_model(self, emails: List[Dict], labels: List[int]) -> Dict:
        """
        Evaluate ML model performance on a test dataset.

        Args:
            emails: List of email dictionaries
            labels: List of labels (0=safe, 1=spam)

        Returns:
            Evaluation metrics dictionary

        Example:
            >>> metrics = classifier.evaluate_model(test_emails, test_labels)
            >>> print(f"Accuracy: {metrics['accuracy']:.2%}")
        """
        try:
            # Extract text
            texts = [self._prepare_text_for_ml(email) for email in emails]

            # Evaluate
            metrics = self.ml_classifier.evaluate(texts, labels)

            return metrics

        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {'error': str(e)}

    def get_model_status(self) -> Dict:
        """
        Get current status of ML and hybrid classifier.

        Returns:
            Dictionary with classifier status information

        Example:
            >>> status = classifier.get_model_status()
            >>> print(status['ml_model_trained'])
            True
        """
        model_info = self.ml_classifier.get_model_info()

        return {
            'hybrid_classifier_ready': True,
            'ml_model_trained': self.ml_classifier.is_trained,
            'ml_weight': self.ml_weight,
            'ml_model_info': model_info,
            'rule_based_ready': True,
        }

    def get_feature_importance(self, top_n: int = 20) -> Dict:
        """
        Get most important features from trained ML model.

        Useful for understanding what patterns the model learned.

        Args:
            top_n: Number of top features to return

        Returns:
            Dictionary with important spam and legitimate features

        Example:
            >>> importance = classifier.get_feature_importance()
            >>> print(importance['spam_features'][:5])
        """
        if not self.ml_classifier.is_trained:
            return {'error': 'ML model not trained'}

        return self.ml_classifier.get_feature_importance(top_n)
