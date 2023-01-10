import subprocess
import sys

import anki.cards
import aqt.qt
import aqt.webview

from aqt import gui_hooks, mw


if sys.platform == 'win32':
    opener = ['explorer',  '/select,']
    action_name = 'Open in Explorer'
elif sys.platform == 'darwin':
    opener = ['open', '-R']
    action_name = 'Show in Finder...'
else:
    opener = ['xdg-open', '-R']
    action_name = 'Open Location'


def reveal_file(filename: str):
    subprocess.Popen(opener + [filename])


current_card: anki.cards.Card = None
def update_current_card(text: str, card: anki.cards.Card, kind: str):
    global current_card
    current_card = card
    return text


def get_filename(pycmd: str, card: anki.cards.Card):
    r'''Turn a 'play:q:0' string into the actual audio file's filename.'''
    play, context, str_idx = pycmd.split(":")
    idx = int(str_idx)
    if context == "q":
        tags = card.question_av_tags()
    else:
        tags = card.answer_av_tags()
    return tags[idx].filename


def on_webview_will_show_context_menu(webview: aqt.webview.AnkiWebView, menu: aqt.qt.QMenu):
    if mw.state != "review":
        return
    def add_menu_option(pycmd: str) -> None:
        if pycmd:
            try:
                filename = get_filename(pycmd, current_card)
                menu.addAction(action_name, lambda *_: reveal_file(filename))
            except AttributeError: # this is a tts not a soundorvideo tag
                pass
    get_audio_pycmd = r'''
function getAudioPycmd() {
    const replayButton = [...document.querySelectorAll('.replay-button')].find((ele) =>
        ele.contains(document.activeElement)
    );
    if (replayButton) {
        const onclick = replayButton.getAttribute('onclick').split(';')[0];
        const pycmd = onclick.match(/pycmd\('(?<pycmd>.+)'\)/).groups.pycmd;
        return pycmd;
    } else {
        return '';
    }
}
getAudioPycmd();
'''
    webview.evalWithCallback(get_audio_pycmd, add_menu_option)


gui_hooks.card_will_show.append(update_current_card)
gui_hooks.webview_will_show_context_menu.append(on_webview_will_show_context_menu)

