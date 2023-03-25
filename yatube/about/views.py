from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['just_title'] = 'Об авторе проекта'
        context['just_text'] = (
            'Тут я размещу информацию о себе,'
            'используя свои умения верстать.'
            'Картинки, блоки, элементы бустрап. '
            'А может быть, просто напишу несколько '
            'абзацев текста. ')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
