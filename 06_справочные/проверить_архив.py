#!/usr/bin/env python3
"""Read-only, offline integrity check for the 2026-09-19 Dubrava archive update.
Uses only the Python 3 standard library. Does not edit files or access the network.
"""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
CONTROL = ROOT / '01_НАЧНИ_ОТСЮДА/КОНТРОЛЬ_СОХРАННОСТИ.json'
PUBLICATION = ROOT / '03-сайт/СВЕРКА_ПУБЛИКАЦИИ.json'
SITE = ROOT / '03-сайт/сайт_текущий'
errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


def file_at(relative):
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents:
        raise ValueError('Путь вне архива: ' + relative)
    return path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.robots = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'meta' and attrs.get('name', '').lower() == 'robots':
            self.robots.append(attrs.get('content', '').lower())
        if attrs.get('id'):
            self.ids.append(attrs['id'])


def sitemap(name):
    return [n.text for n in ET.parse(SITE / name).iter()
            if n.tag.rsplit('}', 1)[-1] == 'loc']


def main():
    control = json.loads(CONTROL.read_text(encoding='utf-8'))
    publication = json.loads(PUBLICATION.read_text(encoding='utf-8'))
    original = control['original_files']
    require(len(original) == 145, 'В манифесте должно быть 145 исходных файлов')
    require(control['deleted_files'] == [], 'В манифесте указаны удаления')
    for item in original:
        p = file_at(item['path'])
        require(p.is_file(), 'Отсутствует исходный файл: ' + item['path'])
        if p.is_file():
            require(digest(p) == item['after_sha256'], 'Файл отличается от обновления: ' + item['path'])
    for item in control['added_files']:
        p = file_at(item['path'])
        require(p.is_file(), 'Отсутствует добавленный файл: ' + item['path'])
        if p.is_file() and item.get('sha256'):
            require(digest(p) == item['sha256'], 'Изменён добавленный файл: ' + item['path'])
    for relative in control['protected_unchanged_files']:
        item = next(x for x in original if x['path'] == relative)
        p = file_at(relative)
        require(p.is_file() and digest(p) == item['before_sha256'], 'Изменён защищённый оригинал: ' + relative)

    require(len(publication['source_files']) == 92, 'Ожидалось 92 файла снимка публикации')
    for item in publication['source_files']:
        p = file_at('03-сайт/сайт_текущий/' + item['path'])
        require(p.is_file() and digest(p) == item['sha256'], 'Снимок расходится с публикацией: ' + item['path'])
    require(len(publication['http_checks']) == 91, 'В журнале должно быть 91 HTTP-сопоставление')
    require(all(x.get('status') == 200 and x.get('matches_source')
                for x in publication['http_checks']), 'Неуспешное прошлое HTTP-сопоставление')

    full = sitemap('sitemap-full.xml')
    main_urls = sitemap('sitemap.xml')
    require(len(full) == len(set(full)) == 26, 'Полная карта должна содержать 26 разных URL')
    require(len(main_urls) == len(set(main_urls)) == 25, 'Основная карта должна содержать 25 разных URL')
    robots = RobotFileParser()
    robots.parse((SITE / 'robots.txt').read_text(encoding='utf-8').splitlines())
    open_urls, closed_urls = set(), set()
    for url in full:
        part = urlsplit(url).path.lstrip('/')
        relative = part + 'index.html' if not part or part.endswith('/') else part
        page = Page()
        page.feed((SITE / relative).read_text(encoding='utf-8'))
        require(page.h1 == 1, 'Не один H1: ' + url)
        require(len(page.ids) == len(set(page.ids)), 'Дубли id: ' + url)
        if any('noindex' in directive for directive in page.robots):
            closed_urls.add(url)
        else:
            open_urls.add(url)
            require(robots.can_fetch('*', url), 'Открытый URL заблокирован robots.txt: ' + url)
    require(closed_urls == {'https://zapahstarosti.ru/nabor/'}, 'Изменился список закрытых контентных URL')
    require(open_urls == set(main_urls), 'Открытые страницы не совпадают с основной картой')

    newer = ROOT / '05_приложение/app/index.html'
    standalone = ROOT / '05_приложение/МЕЧТА_автономная_копия.html'
    require(newer.read_bytes() == standalone.read_bytes(), 'Новая PWA и автономная копия расходятся')
    require(digest(newer) == '1b7bb717edaf6922d4e9e51044b149acee55a4f5518bd44d8ebbf456010a6df1',
            'Новая версия трекера не сохранена побайтово')
    require(newer.stat().st_size == 80825, 'Размер новой PWA изменился')
    require((SITE / 'app/index.html').stat().st_size == 66182, 'Размер опубликованной PWA изменился')
    require(len(list((ROOT / '04_упаковка/финальные_макеты').glob('*.png'))) == 10,
            'Количество PNG-макетов отличается от 10')

    if errors:
        print('Проверка не пройдена:')
        for message in errors:
            print(' - ' + message)
        return 1
    print('Проверка пройдена.')
    print('Все 145 исходных файлов на месте; удалений нет.')
    print('Упаковка, скрипты и новая PWA сохранены побайтово: 26 защищённых файлов.')
    print('Снимок соответствует 92 файлам указанного коммита; 25 из 26 контентных URL открыты.')
    print('Новая версия приложения и автономная копия совпадают; опубликованная сохранена отдельно.')
    print('91 HTTP-проверка относится к дате в журнале; новых сетевых запросов этот скрипт не делал.')
    print('Это проверка архивного обновления, не испытание продукции и не полный тест функций сайта.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        print('Не удалось проверить архив: ' + str(exc), file=sys.stderr)
        sys.exit(1)
