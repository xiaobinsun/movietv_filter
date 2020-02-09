# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Celebrity(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'celebrity'


class MovieTv(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    region = models.CharField(max_length=30, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movie_tv'


class Participant(models.Model):
    subject = models.ForeignKey(MovieTv, models.DO_NOTHING, primary_key=True)
    celebrity = models.ForeignKey(Celebrity, models.DO_NOTHING)
    role = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'participant'
        unique_together = (('subject', 'celebrity', 'role'),)


class Score(models.Model):
    id = models.ForeignKey(MovieTv, models.DO_NOTHING, db_column='id', primary_key=True)
    score_date = models.DateField()
    score = models.FloatField()
    votes = models.IntegerField()
    five_star = models.FloatField()
    four_star = models.FloatField()
    three_star = models.FloatField()
    two_star = models.FloatField()
    one_star = models.FloatField()

    class Meta:
        managed = False
        db_table = 'score'
        unique_together = (('id', 'score_date'),)


class Seed(models.Model):
    sid = models.IntegerField(primary_key=True)
    stype = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'seed'


class Tag(models.Model):
    id = models.ForeignKey(MovieTv, models.DO_NOTHING, db_column='id', primary_key=True)
    tag = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'tag'
        unique_together = (('id', 'tag'),)
