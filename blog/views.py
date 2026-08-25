from collections import defaultdict

from django.db.models import Count, F, Window
from django.db.models.functions import RowNumber
from django.views.generic import ListView

from .models import BlogPost, Topic


class HtmxListView(ListView):
    paginate_by = 10
    partial_template_name = None

    def get_template_names(self):
        if (
            self.request.headers.get('HX-Request') == 'true'
            and self.request.headers.get('HX-History-Restore-Request') != 'true'
        ):
            return [self.partial_template_name]
        return super().get_template_names()

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_number = self.kwargs.get(
            self.page_kwarg, self.request.GET.get(self.page_kwarg)
        )
        page = paginator.get_page(page_number)
        return paginator, page, page.object_list, page.has_other_pages()


class TopicListView(HtmxListView):
    model = Topic
    template_name = 'blog/topics.html'
    partial_template_name = 'blog/partials/topic_results.html'

    def get_queryset(self):
        self.query = self.request.GET.get('q', '').strip()
        topics = super().get_queryset()
        return topics.filter(title__icontains=self.query) if self.query else topics

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page_obj']
        topic_ids = [topic.id for topic in page.object_list]
        authors_by_topic = defaultdict(list)

        if topic_ids:
            author_counts = (
                BlogPost.objects.filter(topic_id__in=topic_ids)
                .values('topic_id', 'author_id', 'author__name')
                .annotate(post_count=Count('id'))
                .annotate(
                    topic_rank=Window(
                        expression=RowNumber(),
                        partition_by=F('topic_id'),
                        order_by=(
                            F('post_count').desc(),
                            F('author__name').asc(),
                            F('author_id').asc(),
                        ),
                    )
                )
                .filter(topic_rank__lte=3)
                .order_by('topic_id', 'topic_rank')
            )
            for row in author_counts:
                authors_by_topic[row['topic_id']].append(
                    {
                        'name': row['author__name'],
                        'post_count': row['post_count'],
                    }
                )

        for topic in page.object_list:
            topic.top_authors = authors_by_topic[topic.id]

        context['q'] = self.query
        return context


class PostListView(HtmxListView):
    queryset = BlogPost.objects.select_related('author', 'topic')
    template_name = 'blog/posts.html'
    partial_template_name = 'blog/partials/post_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page_obj']
        author_ids = {post.author_id for post in page.object_list}
        topics_by_author = defaultdict(list)

        if author_ids:
            author_topics = (
                BlogPost.objects.filter(author_id__in=author_ids)
                .values('author_id', 'topic_id', 'topic__title')
                .order_by('author_id', 'topic__title', 'topic_id')
                .distinct()
            )
            for row in author_topics:
                topics_by_author[row['author_id']].append(
                    {'id': row['topic_id'], 'title': row['topic__title']}
                )

        for post in page.object_list:
            post.other_topics = [
                topic
                for topic in topics_by_author[post.author_id]
                if topic['id'] != post.topic_id
            ]

        return context
