from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from blog.views import post_list, post_detail, post_share, post_comment, post_search
from django.contrib.auth.models import User
from blog.models import Post, Comment

class TestUrls(SimpleTestCase):

    def test_post_list_url(self):
        url = reverse('blog:post_list')
        self.assertEquals(resolve(url).func, post_list)

    def test_post_detail_url(self):
        url = reverse('blog:post_detail', args=['2022', '12', '31', 'some-post'])
        self.assertEquals(resolve(url).func, post_detail)

    def test_post_share_url(self):
        url = reverse('blog:post_share', args=['1'])
        self.assertEquals(resolve(url).func, post_share)

    def test_post_comment_url(self):
        url = reverse('blog:post_comment', args=['1'])
        self.assertEquals(resolve(url).func, post_comment)

    def test_post_search_url(self):
        url = reverse('blog:post_search')
        self.assertEquals(resolve(url).func, post_search)


class PostTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(title='Test Post', author=self.user, slug='test-post', body='Test Body', status=Post.Status.PUBLISHED)
        self.comment = Comment.objects.create(post=self.post, name='Test User', email='test@example.com', body='Test comment')

    def tearDown(self):
        self.user.delete()
        self.post.delete()
        self.comment.delete()


class PostModelTest(PostTestBase):

    def test_post_content(self):
        expected_object_name = f'{self.post.title}'
        self.assertEquals(expected_object_name, 'Test Post')


class CommentModelTest(PostModelTest):

    def test_comment_content(self):
        expected_object_name = f'Comment by {self.comment.name} on {self.comment.post}'
        self.assertEquals(expected_object_name, 'Comment by Test User on Test Post')


class BlogTest(PostModelTest):

    def test_PostListView(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/list.html')
        self.assertContains(response, 'Test Post')

    def test_post_list(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_detail(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_share_GET(self):
        response = self.client.get(reverse('blog:post_share', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/share.html')

    def test_post_share_POST(self):
        response = self.client.post(reverse('blog:post_share', args=[self.post.id]), {'name': 'Test Name', 'email': 'test@example.com', 'to': 'to@example.com', 'comments': 'Test comment'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"Test Post" was successfully sent')

    def test_post_comment(self):
        self.client.post(reverse('blog:post_comment', args=[self.post.id]), {'name': 'Test Name', 'email': 'test@example.com', 'body': 'Test comment'})
        comment = Comment.objects.get(post=self.post, name='Test Name')
        self.assertEqual(comment.email, 'test@example.com')
        self.assertEqual(comment.body, 'Test comment')

    def test_post_search(self):
        response = self.client.get(reverse('blog:post_search') + '?query=test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

