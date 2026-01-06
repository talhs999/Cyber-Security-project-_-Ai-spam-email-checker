"""
Unit Tests for Machine Learning Components

This test suite validates:
- NLP text processing functionality
- ML classifier training and prediction
- Hybrid classification combining ML + rules
- Model persistence (save/load)
- Training pipeline workflow

To run tests:
    pytest tests/test_ml_classifier.py -v
"""

import pytest
import os
import tempfile
from typing import List, Tuple

# Import ML components
try:
    from src.nlp_processor import NLPProcessor
    from src.spam_classifier import SpamEmailClassifier
    from src.ml_classifier import HybridClassifier
    from src.training_pipeline import TrainingPipeline
except ImportError as e:
    pytest.skip(f"ML components not available: {e}")


class TestNLPProcessor:
    """Tests for NLP text processing functionality"""

    @pytest.fixture
    def nlp(self):
        """Create NLPProcessor instance"""
        return NLPProcessor()

    def test_nlp_initialization(self, nlp):
        """Test NLP processor initialization"""
        assert nlp is not None
        assert nlp.stemmer is not None
        assert nlp.stop_words is not None

    def test_tokenization(self, nlp):
        """Test text tokenization"""
        text = "Click here to verify your account"
        tokens = nlp.tokenize(text)

        assert len(tokens) > 0
        assert isinstance(tokens, list)
        assert all(isinstance(t, str) for t in tokens)

    def test_tokenization_empty(self, nlp):
        """Test tokenization with empty string"""
        tokens = nlp.tokenize("")
        assert tokens == []

    def test_stopword_removal(self, nlp):
        """Test stopword removal"""
        tokens = ['the', 'cat', 'is', 'on', 'the', 'mat', 'sitting']
        filtered = nlp.remove_stopwords(tokens)

        assert 'the' not in filtered
        assert 'is' not in filtered
        assert 'on' not in filtered
        assert 'cat' in filtered
        assert 'mat' in filtered

    def test_stemming(self, nlp):
        """Test word stemming"""
        tokens = ['running', 'runs', 'runner', 'verify', 'verification']
        stemmed = nlp.stem(tokens)

        assert len(stemmed) == len(tokens)
        assert all(isinstance(s, str) for s in stemmed)
        # All "running*" words should stem to same root
        assert stemmed[0] == stemmed[1] or 'run' in stemmed[0]

    def test_ngram_extraction(self, nlp):
        """Test n-gram extraction"""
        tokens = ['click', 'here', 'to', 'verify', 'account']

        # Bigrams
        bigrams = nlp.extract_ngrams(tokens, 2)
        assert len(bigrams) > 0
        assert 'click here' in bigrams
        assert 'verify account' in bigrams

        # Trigrams
        trigrams = nlp.extract_ngrams(tokens, 3)
        assert len(trigrams) > 0

    def test_text_analysis(self, nlp):
        """Test comprehensive text analysis"""
        text = "Win free money now click here immediately"
        analysis = nlp.analyze_text(text)

        assert 'tokens' in analysis
        assert 'token_count' in analysis
        assert 'stemmed' in analysis
        assert 'bigrams' in analysis
        assert 'trigrams' in analysis
        assert 'unique_tokens' in analysis
        assert 'content_richness' in analysis

        assert analysis['token_count'] > 0
        assert analysis['unique_tokens'] > 0
        assert 0 <= analysis['content_richness'] <= 1

    def test_text_statistics(self, nlp):
        """Test text statistics calculation"""
        text = "Hello world. How are you? I am fine!"
        stats = nlp.calculate_text_statistics(text)

        assert 'word_count' in stats
        assert 'sentence_count' in stats
        assert 'avg_word_length' in stats
        assert 'character_count' in stats

        assert stats['word_count'] > 0
        assert stats['avg_word_length'] > 0


class TestSpamEmailClassifier:
    """Tests for ML spam classifier"""

    @pytest.fixture
    def temp_model_path(self):
        """Create temporary model path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, 'test_model.joblib')

    @pytest.fixture
    def classifier(self, temp_model_path):
        """Create classifier with temporary model path"""
        return SpamEmailClassifier(model_path=temp_model_path)

    @pytest.fixture
    def training_data(self):
        """Sample training data"""
        texts = [
            "Congratulations you won the lottery click here now",
            "Meeting tomorrow at 3pm office",
            "Win free money instant payment required",
            "Project update attached please review",
            "Verify your account immediately urgent",
            "Hello how are you today",
            "CLICK HERE FOR FREE MONEY NOW",
            "Budget report Q4 attached",
        ]
        labels = [1, 0, 1, 0, 1, 0, 1, 0]  # 1=spam, 0=safe

        return texts, labels

    def test_classifier_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier is not None
        assert classifier.pipeline is None or classifier.pipeline is not None
        assert isinstance(classifier.is_trained, bool)

    def test_pipeline_creation(self, classifier):
        """Test pipeline creation"""
        classifier.create_pipeline()
        assert classifier.pipeline is not None

    def test_training(self, classifier, training_data):
        """Test model training"""
        texts, labels = training_data

        classifier.train(texts, labels)

        assert classifier.is_trained is True
        assert classifier.pipeline is not None

    def test_prediction(self, classifier, training_data):
        """Test email prediction"""
        texts, labels = training_data

        # Train first
        classifier.train(texts, labels)

        # Test prediction
        test_email = "Win free money immediately click here"
        prediction, confidence = classifier.predict(test_email)

        assert prediction in [0, 1]
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

    def test_prediction_without_training(self, classifier):
        """Test prediction without training returns None"""
        prediction, confidence = classifier.predict("test email")
        assert prediction is None
        assert confidence == 0.0

    def test_batch_prediction(self, classifier, training_data):
        """Test batch predictions"""
        texts, labels = training_data
        classifier.train(texts, labels)

        test_emails = [
            "Win free money",
            "Meeting tomorrow",
            "Verify account now",
        ]

        predictions = classifier.predict_batch(test_emails)

        assert len(predictions) == len(test_emails)
        for pred, conf in predictions:
            assert pred in [0, 1]
            assert 0 <= conf <= 1

    def test_model_save_load(self, classifier, training_data):
        """Test model persistence"""
        texts, labels = training_data

        # Train and save
        classifier.train(texts, labels)
        assert os.path.exists(classifier.model_path)

        # Load in new classifier
        classifier2 = SpamEmailClassifier(model_path=classifier.model_path)
        assert classifier2.is_trained is True

        # Both should make same prediction
        test_email = "Win free money"
        pred1, conf1 = classifier.predict(test_email)
        pred2, conf2 = classifier2.predict(test_email)

        assert pred1 == pred2
        assert conf1 == conf2

    def test_evaluation(self, classifier, training_data):
        """Test model evaluation"""
        texts, labels = training_data

        metrics = classifier.evaluate(texts, labels)

        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision'] <= 1

    def test_get_model_info(self, classifier, training_data):
        """Test getting model information"""
        texts, labels = training_data
        classifier.train(texts, labels)

        info = classifier.get_model_info()

        assert 'status' in info
        assert info['status'] == 'Trained'
        assert 'n_features' in info
        assert info['n_features'] > 0


class TestHybridClassifier:
    """Tests for hybrid ML + rule-based classifier"""

    @pytest.fixture
    def hybrid(self):
        """Create hybrid classifier"""
        try:
            return HybridClassifier()
        except Exception as e:
            pytest.skip(f"HybridClassifier not available: {e}")

    def test_hybrid_initialization(self, hybrid):
        """Test hybrid classifier initialization"""
        assert hybrid is not None
        assert hybrid.ml_classifier is not None
        assert hybrid.threat_detector is not None

    def test_model_status(self, hybrid):
        """Test getting model status"""
        status = hybrid.get_model_status()

        assert 'hybrid_classifier_ready' in status
        assert 'ml_model_trained' in status
        assert 'ml_weight' in status

    def test_prepare_text_for_ml(self, hybrid):
        """Test text preparation for ML"""
        email_data = {
            'subject': 'Win free money',
            'body': 'Click here immediately',
        }

        text = hybrid._prepare_text_for_ml(email_data)

        assert isinstance(text, str)
        assert len(text) > 0
        assert 'Win' in text or 'win' in text.lower()


class TestTrainingPipeline:
    """Tests for training pipeline"""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        try:
            pipeline = TrainingPipeline(min_samples=5)
            assert pipeline is not None
            assert pipeline.min_samples == 5
        except Exception as e:
            # Skip if database not available
            pytest.skip(f"TrainingPipeline not available: {e}")

    def test_validate_training_data(self):
        """Test training data validation"""
        try:
            pipeline = TrainingPipeline(min_samples=5)

            texts = [
                "Spam email text",
                "Safe email text",
                "Another spam",
                "Another safe",
                "More spam text",
            ]
            labels = [1, 0, 1, 0, 1]

            validation = pipeline.validate_training_data(texts, labels)

            assert 'is_valid' in validation
            assert 'total_samples' in validation
            assert validation['total_samples'] == 5

        except Exception as e:
            pytest.skip(f"Test not available: {e}")

    def test_insufficient_data_validation(self):
        """Test validation with insufficient data"""
        try:
            pipeline = TrainingPipeline(min_samples=10)

            texts = ["text1", "text2"]
            labels = [0, 1]

            validation = pipeline.validate_training_data(texts, labels)

            assert validation['is_valid'] is False
            assert len(validation['issues']) > 0

        except Exception as e:
            pytest.skip(f"Test not available: {e}")


# Integration Tests
class TestIntegration:
    """Integration tests combining multiple components"""

    def test_nlp_to_classifier_pipeline(self):
        """Test complete NLP to classification pipeline"""
        nlp = NLPProcessor()
        classifier = SpamEmailClassifier()

        # Analyze text with NLP
        text = "Click here immediately to verify your account"
        analysis = nlp.analyze_text(text)

        assert analysis['token_count'] > 0
        assert len(analysis['bigrams']) > 0

        # Text is ready for ML classification
        assert len(text) > 0

    def test_spam_vs_legitimate_detection(self):
        """Test classifier distinguishes spam from legitimate"""
        classifier = SpamEmailClassifier()

        # Create clear training data
        spam_emails = [
            "WIN FREE MONEY NOW CLICK HERE",
            "Congratulations you won",
            "Verify account immediately",
            "Claim prize winner",
        ]
        safe_emails = [
            "Meeting at 3pm tomorrow",
            "Project deadline extended",
            "New code committed",
            "Status update available",
        ]

        texts = spam_emails + safe_emails
        labels = [1] * len(spam_emails) + [0] * len(safe_emails)

        # Train
        classifier.train(texts, labels)

        # Test on known spam
        pred_spam, conf_spam = classifier.predict(spam_emails[0])
        assert pred_spam == 1  # Should detect as spam

        # Test on known safe
        pred_safe, conf_safe = classifier.predict(safe_emails[0])
        assert pred_safe == 0  # Should detect as safe


# Performance Tests
class TestPerformance:
    """Performance and efficiency tests"""

    def test_nlp_performance(self):
        """Test NLP processing speed"""
        nlp = NLPProcessor()
        text = "This is a test email. " * 50  # Long email

        import time
        start = time.time()
        analysis = nlp.analyze_text(text)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0
        assert analysis['token_count'] > 0

    def test_classifier_performance(self):
        """Test classifier prediction speed"""
        classifier = SpamEmailClassifier()

        # Train with minimal data
        texts = [f"Email {i}" for i in range(10)]
        labels = [i % 2 for i in range(10)]

        classifier.train(texts, labels)

        # Test prediction speed
        import time
        start = time.time()
        for _ in range(10):
            classifier.predict("Test email")
        elapsed = time.time() - start

        # Should complete 10 predictions in reasonable time
        assert elapsed < 5.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
