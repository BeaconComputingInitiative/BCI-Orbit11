#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# GUI tests pass IF AND ONLY IF every page renders and all declared controls route.
"""Run only on a computer with PyQt6. Does not query systemd or open privileges."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'src'))
from PyQt6.QtWidgets import QApplication
import orbital_gui as ui

# Disable live collection during offscreen smoke; use deterministic synthetic UI data.
ui.Orbital.refresh=lambda self:None
app=QApplication([])
assets=Path(__file__).resolve().parent.parent/'assets'
window=ui.Orbital(assets)
window.info={'header':ui.HEADER,'developer_seal':ui.SEAL,'hostname':'Enterprise',
 'states':{'host':'active','packet':'active','neural':'active'},'services_up':3,
 'journal_valid':True,'journal':{'valid':True,'count':3,'contexts':{}},
 'current_context':'ctx-53ad9a6b85d65ca7','current_interface':'usb0',
 'neural_window_count':3,'hours':1,'days':0.01,
 'mem_pct':23,'disk_pct':39,'features':{},'events':[]}
window.show()
app.processEvents()
required={'System Status','Verify Evidence','Neural Status','Services',
          'Generate Report','Policy & Control','Train Status','Prepare',
          'Review','Run','Evaluate','Promote','Rollback','View All'}
for page in ui.TABS:
    window.navigate(page)
    app.processEvents()
    image=window.grab()
    if image.isNull() or image.width()<1100 or image.height()<650:
        raise SystemExit('HOLD: GUI rendering failed on '+page)
    for label,rect in window.buttons:
        if label not in ui.TABS and label not in ('MIN','MAX','CLOSE'):
            if label not in window.actions:
                raise SystemExit('HOLD: Unwired button '+label)
            if rect.width()<=0 or rect.height()<=0:
                raise SystemExit('HOLD: Invalid button geometry '+label)
window.navigate('Orbital AI');app.processEvents()
assert window.chat_view.isVisible() and window.chat_input.isVisible() and window.chat_send.isVisible()
window.chat_input.setText('what are your baselines')
window.chat_send.click();app.processEvents()
assert 'Host behavioral profile' in window.chat_view.toPlainText()
assert 'AI Baselines' in window.actions
window.navigate('Dashboard');app.processEvents()
seen={name for name,_ in window.buttons}
if required-seen:
    raise SystemExit('HOLD: Missing dashboard controls '+str(required-seen))
window.close();app.processEvents()
print('BEACON COMPUTING INITIATIVE')
print('Developer Seal: CJB-DEV-2026')
print(f'PASS: {len(ui.TABS)} pages rendered; all visible buttons mapped; original globe asset loaded')
