from django.db import models
from django.contrib.auth.models import User


class RoadmapProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    career_goal = models.CharField(max_length=100)
    completed_steps = models.JSONField(default=list)

    class Meta:
        unique_together = ('user', 'career_goal')

    def __str__(self):
        return f"{self.user.username} - {self.career_goal}"


class SkillAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scores = models.JSONField(default=dict)
    average_score = models.FloatField()
    level = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.level}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    career_goal = models.CharField(max_length=100)
    lesson_number = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'career_goal', 'lesson_number')

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.career_goal} - "
            f"Lesson {self.lesson_number}"
        )


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.activity}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"