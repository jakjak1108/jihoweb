import os
import logging

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.urls import reverse
from django.utils import timezone


class SiteUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        # 일반 사용자 생성 함수
        if not username:
            raise ValueError("사용자는 사용자 이름이 있어야 합니다")
        user = self.model(username=self.normalize_email(username),)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        # 어드민 사용자 생섬 함수
        user = self.create_user(username, password=password,)
        user.is_admin = True
        user.save(using=self._db)
        return user


class SiteUser(AbstractBaseUser, PermissionsMixin):
    # 사용자 모델

    username = models.CharField("아이디", max_length=20, unique=True)
    date_joined = models.DateTimeField("가입일", default=timezone.now)
    date_modified = models.DateTimeField("최종 수정일", auto_now=True)
    is_active = models.BooleanField("활성 사용자", default=True)
    is_admin = models.BooleanField("관리자", default=False)
    # 부가 사용자 정보
    name = models.CharField("이름", max_length=20, blank=True, null=True)
    email = models.EmailField(
        verbose_name="이메일", max_length=255, blank=True, null=True,
    )

    objects = SiteUserManager()

    USERNAME_FIELD = "username"

    class Meta:
        ordering = ["-date_joined"]

    def get_full_name(self):
        # 사용자는 사용자 이름으로 식별됩니다
        return self.username

    def get_short_name(self):
        # 사용자는 사용자 이름으로 식별됩니다
        return self.username

    def __str__(self):
        return "%s | %s" % (self.name, self.username)

    def has_perm(self, perm, obj=None):
        "사용자는 특정한 허가를 가지고 있는가?"
        # 가능한 가장 간단한 대답: 네, 항상
        return True

    def has_module_perms(self, app_label):
        "사용자는 앱 'app_label'을 볼 수 있는 허가를 가지고 있는가?"
        # 가능한 가장 간단한 대답: 네, 항상
        return True

    @property
    def is_staff(self):
        "사용자는 스태프의 일원인가?"
        # 가능한 가장 간단한 대답: 모든 관리자는 스태프이다
        return self.is_admin


class Board(models.Model):
    # 게시판

    name = models.CharField("게시판 이름", max_length=20, unique=True)
    order = models.PositiveIntegerField("정렬순서", default=0)
    date_created = models.DateTimeField("생성일", default=timezone.now)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("board-detail", kwargs={"pk": self.pk})


class Post(models.Model):
    # 게시글

    board = models.ForeignKey(
        Board, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="게시판"
    )
    author = models.ForeignKey(
        SiteUser, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="작성자"
    )
    title = models.CharField("제목", max_length=200)
    is_notice = models.BooleanField("공지", default=False)
    date_created = models.DateTimeField("작성일", default=timezone.now)
    date_modified = models.DateTimeField("최종 수정일", auto_now=True)
    content = models.TextField("내용")
    views = models.PositiveIntegerField("조회수", default=0)

    class Meta:
        ordering = ["-is_notice", "-date_created"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})
