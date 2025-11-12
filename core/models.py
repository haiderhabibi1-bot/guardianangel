from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    """
    Basic customer profile.

    Keep it simple and stable: one-to-one with the auth user plus a counter
    for how many free public questions they have.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    free_public_questions_remaining = models.PositiveIntegerField(default=2)

    def __str__(self) -> str:
        return f"CustomerProfile({self.user.username})"


class LawyerProfile(models.Model):
    """
    Basic lawyer profile used on the Lawyers List page.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lawyer_profile",
    )
    speciality = models.CharField(max_length=255, blank=True)
    bar_number = models.CharField(max_length=64, blank=True)
    years_of_practice = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    fee_per_chat = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_approved = models.BooleanField(
        default=True
    )  # treat as approved; keeps Lawyers List working
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"LawyerProfile({self.user.username})"

    @property
    def name(self) -> str:
        full = (self.user.get_full_name() or "").strip()
        return full or self.user.username


class PublicQuestion(models.Model):
    """
    Public questions shown on the Public Questions page.

    Template expects 'question_text' and 'answer' accessible via q.answer.
    """
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_questions",
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"PublicQuestion({self.pk})"

    @property
    def answer(self) -> str:
        """
        Used directly in the template as q.answer.
        """
        try:
            return self.answer_obj.answer_text
        except PublicAnswer.DoesNotExist:
            return ""


class PublicAnswer(models.Model):
    """
    Answer to a PublicQuestion by a lawyer.
    """
    question = models.OneToOneField(
        PublicQuestion,
        on_delete=models.CASCADE,
        related_name="answer_obj",
    )
    lawyer = models.ForeignKey(
        LawyerProfile,
        on_delete=models.CASCADE,
        related_name="public_answers",
    )
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"PublicAnswer(q={self.question_id}, lawyer={self.lawyer.user.username})"


class ChatRoom(models.Model):
    """
    Simple chat room between a customer and a lawyer.
    (Structure only; hook-up/payment logic can be added later.)
    """
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="chat_rooms",
    )
    lawyer = models.ForeignKey(
        LawyerProfile,
        on_delete=models.CASCADE,
        related_name="chat_rooms",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"ChatRoom({self.customer.user.username} ↔ {self.lawyer.user.username})"


class ChatMessage(models.Model):
    """
    Messages inside a ChatRoom.
    """
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"ChatMessage(room={self.room_id}, sender={self.sender.username})"
