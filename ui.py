import math


def justify_line(text, width):
  # break string into lines not longer than width
  words = text.split(' ')
  lines = []
  current_line = []
  for i, word in enumerate(words):
    current_line.append(word)
    if (word is words[-1]) or (len(' '.join(current_line + [words[i+1]])) > width):
      lines.append(current_line)
      current_line = []

  # pad lines to final width
  for i, line in enumerate(lines):
    if line is lines[-1]:
      lines[i] = ' '.join(line)
    else:
      spaces_left = width - len(''.join(line))
      for j, word in enumerate(line[:-1]):
        voids_left = len(line[j:-1])
        void_length = int(math.ceil(1.0 * spaces_left / voids_left))
        line[j] += ' ' * void_length
        spaces_left -= void_length
      lines[i] = ''.join(line)

  return '\n'.join(lines)


def format_text_block(text, cutoff=1000, width=60):
  """Return at most `cutoff` chars of `text`, justified to given width"""
  text = text.replace('\t', '')
  if len(text) > cutoff:
    text = text[:cutoff] + '[...]'
  formatted = []
  for line in text.split('\n'):
    formatted.append(justify_line(line, width))
  return '\n\n'.join(formatted)
