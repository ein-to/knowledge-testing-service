from django.db import models
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Theme(models.Model):
    theme_name = models.CharField(max_length=60)

    def __str__(self):
        return self.theme_name

class Question(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)

    def __str__(self):
        theme = Theme.objects.get(theme_name=self.theme)
        theme = theme.theme_name
        return f"{theme} - {self.question_text}"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=400)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.answer_text}"

    def save(self, *args, **kwargs):
        if Answer.objects.filter(question=self.question, correct=False).count()==3 and Answer.objects.filter(question=self.question, correct=True).count()==0 and self.correct==False:
            raise ValidationError('Необходимо ввести минимум 1 (один) правильный вариант ответа')
        if Answer.objects.filter(question=self.question).count()==4:
            raise ValidationError('Количество вариантов ответов достигло максимума = 4')
        if Answer.objects.filter(question=self.question, correct=True).count()==3 and self.correct == True:
            raise ValidationError('Количество правильных вариантов ответов не может превышать 3 (трех)')
        else:
            super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if Answer.objects.filter(question=self.question, correct=False).count()==3 and Answer.objects.filter(question=self.question, correct=True).count()==0 and self.correct==False:
            raise ValidationError('Необходимо ввести минимум 1 (один) правильный вариант ответа')
        if Answer.objects.filter(question=self.question).count()==4:
            raise ValidationError('Количество вариантов ответов достигло максимума = 4')
        if Answer.objects.filter(question=self.question, correct=True).count()==3 and self.correct == True:
            raise ValidationError('Количество правильных вариантов ответов не может превышать 3 (трех)')
        else:
            super().clean(*args, **kwargs)

class Results_details(models.Model):
    username = models.CharField(max_length=60)
    theme = models.CharField(max_length=60)
    date = models.DateTimeField()
    question_id = models.IntegerField()
    correct = models.BooleanField()

    def __str__(self):
        theme = Theme.objects.get(id=self.theme)
        return f"{self.username} - {theme.theme_name}"
