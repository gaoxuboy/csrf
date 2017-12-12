from django.db import models


class UserInfo(models.Model):
    """
    用户表
    """
    user = models.CharField(max_length=32,unique=True)
    pwd = models.CharField(max_length=64)


class Room(models.Model):
    """
    会议室表
    """
    caption = models.CharField(max_length=32)
    num = models.IntegerField()


class Book(models.Model):
    """
    会议室预定信息
    """
    user = models.ForeignKey('UserInfo')
    room = models.ForeignKey('Room')
    date = models.DateField()
    time_choices = (
        (1, '8:00'),
        (2, '9:00'),
        (3, '10:00'),
        (4, '11:00'),
        (5, '12:00'),
        (6, '13:00'),
        (7, '14:00'),
        (8, '15:00'),
        (9, '16:00'),
        (10, '17:00'),
        (11, '18:00'),
        (12, '19:00'),
        (13, '20:00'),
    )
    time_id = models.IntegerField(choices=time_choices)

    class Meta:
        unique_together = (
            ('room','date','time_id'),
        )










