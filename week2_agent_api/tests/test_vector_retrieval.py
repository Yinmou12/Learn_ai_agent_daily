import unittest

from app.services.vector_retrieval_service import (
    VECTOR_DIMENSIONS,
    cosine_similarity,
    vectorize_text,
)


class VectorRetrievalTest(unittest.TestCase):
    def test_same_vectors_have_similarity_one(self) -> None:
        vector = vectorize_text("FastAPI Depends 依赖注入")

        similarity = cosine_similarity(vector, vector)

        self.assertAlmostEqual(similarity, 1.0, places=6)

    def test_orthogonal_vectors_have_similarity_zero(self) -> None:
        similarity = cosine_similarity(
            [1.0, 0.0],
            [0.0, 1.0],
        )

        self.assertEqual(similarity, 0.0)

    def test_vector_dimension_is_stable(self) -> None:
        short_vector = vectorize_text("Python")
        long_vector = vectorize_text("FastAPI SQLAlchemy Depends Pydantic")

        self.assertEqual(len(short_vector), VECTOR_DIMENSIONS)
        self.assertEqual(len(long_vector), VECTOR_DIMENSIONS)

    def test_different_dimensions_raise_error(self) -> None:
        with self.assertRaises(ValueError):
            cosine_similarity(
                [1.0, 0.0],
                [1.0, 0.0, 0.0],
            )


if __name__ == "__main__":
    unittest.main()
