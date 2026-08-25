from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=120, unique=True)
    age = models.PositiveIntegerField()

    class Meta:
        ordering = ('name', 'id')

    def __str__(self):
        return self.name


class Topic(models.Model):
    title = models.CharField(max_length=160, unique=True)

    class Meta:
        ordering = ('title', 'id')

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    title = models.CharField(max_length=240)
    content = models.TextField()
    publication_date = models.DateTimeField()
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='posts',
    )

    class Meta:
        ordering = ('-publication_date', '-id')
        indexes = [
            models.Index(fields=('topic', 'author'), name='post_topic_author_idx'),
            models.Index(fields=('author', 'topic'), name='post_author_topic_idx'),
            models.Index(
                fields=('-publication_date', '-id'),
                name='post_newest_idx',
            ),
        ]

    def __str__(self):
        return self.title
