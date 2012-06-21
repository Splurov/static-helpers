import os
import re

def get_media_type(import_rule, url_end):
    url_end += 1
    if url_end < len(import_rule):
        media_type = import_rule[url_end:].strip()
    else:
        media_type = ''
    return media_type

def resolve_imports(path):
    content = open(path).read()
    if content.find('@') == -1:
        return content
    dir = os.path.dirname(path)
    result = []
    l = len(content)
    i = 0
    while i < l:
        if content[i] == '/' and content[i + 1] == '*':
            end = content.find('*/', i + 2)
            if end == -1:
                result.append(content[i:])
                break

            result.append(content[i : end + 2])
            i = end + 2
        elif content[i] in [' ', '\t', '\n', '\r', '\f']:
            result.append(content[i])
            i += 1
        elif content[i] == '@':
            end = content.find(' ', i + 1)
            if end == -1:
                result.append(content[i:])
                break

            type = content[i + 1:end]
            if type == 'charset':
                end = content.find(';', i + 1)
                if end == -1:
                    result.append(content[i:])
                    break

                result.append(content[i : end + 1])
                i = end + 1
            elif type == 'import':
                end = content.find(';', i + 1)
                if end == -1:
                    result.append(content[i:])
                    break

                import_rule = content[i + 8:end].strip()
                if import_rule[0] == '\'':
                    url_end = import_rule.find('\'', 1)
                    if url_end == -1:
                        result.append(content[i : end + 1])
                        i = end + 1
                        continue
                    url = import_rule[1:url_end]
                    media_type = get_media_type(import_rule, url_end)
                elif import_rule[0] == '"':
                    url_end = import_rule.find('"', 1)
                    if url_end == -1:
                        result.append(content[i : end + 1])
                        i = end + 1
                        continue
                    url = import_rule[1:url_end]
                    media_type = get_media_type(import_rule, url_end)
                else:
                    m = re.search('^url\([ \t\b\r\f]?([\'"])?(.+?)\\1?[ \t\b\r\f]?\)(.*)$', import_rule)
                    if m is None:
                        result.append(content[i : end + 1])
                        i = end + 1
                        continue
                    url = m.group(2)
                    media_type = m.group(3).strip()

                imported_content = resolve_imports(os.path.realpath(os.path.join(dir, url)))
                if media_type not in ['', 'all']:
                    imported_content = '@media %s {%s}' % (media_type, imported_content)
                result.append(imported_content)
                i = end + 1
            else:
                result.append(content[i:])
                break
        else:
            result.append(content[i:])
            break

    return ''.join(result)

def parse(path):
    result = resolve_imports(os.path.realpath(path))

    return result
