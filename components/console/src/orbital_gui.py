#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Orbital GUI v0.8.3 — Repair worker lifecycle and use native, single-layer controls.
# Dispatch an action IF AND ONLY IF the verified backend and operator gates permit it.
"""Screenshot-aligned Orbital desktop console with the original pixel-accurate globe.

Unlike 0.7.0, all dashboard panels are painted natively instead of drawing
labels on top of a static screenshot. All visible controls have an action or
explicit HOLD explanation, and no GUI refresh performs a privileged action.
"""
from __future__ import annotations
import json
import math
import os
from datetime import datetime
from pathlib import Path
import sys
import time
from PyQt6.QtCore import Qt, QRectF, QPointF, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QApplication,QWidget,QMessageBox,QPlainTextEdit,QDialog,
                             QVBoxLayout,QLabel,QPushButton,QFileDialog,QHBoxLayout,QComboBox,QLineEdit)
from orbital_backend import (HEADER,SEAL,VERSION,HOME,snapshot,write_operator_report,
                             net_bytes,NEURAL,JOURNAL)
from orbital_ai import respond as ai_respond, model_state as ai_model_state, score_argv as ai_score_argv
from orbital_actions import (Hold,verified_preparation_status,make_candidate,
        review_candidate,neural_command,host_evidence,packet_evidence_with_polkit,
        service_logs)

W,H=1672,941
WHITE=QColor('#F4F8FB');CYAN=QColor('#00E5FF');GREEN=QColor('#36EF9A')
MUTED=QColor('#97B5CC');PURPLE=QColor('#C688FF');RED=QColor('#FF6983')
TABS=['Dashboard','Sensors','Context','Evidence','Neural Core','Orbital AI','Training',
      'Alerts','Control Plane','Reports','Settings']
GLYPHS=['⌂','◎','⬡','▤','◈','✧','◇','△','☷','▣','⚙']


def short(value, size=28):
    s=str(value)
    return s if len(s)<=size else s[:size-1]+'…'


class Poller(QThread):
    collected=pyqtSignal(object)
    def run(self):
        try:
            value=snapshot()
        except Exception as exc:
            value={'error':f'{type(exc).__name__}: {exc}'[:200]}
        self.collected.emit(value)


class Operation(QThread):
    complete=pyqtSignal(str,str,bool)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.action='';self.argv=[]
    def configure(self,name,argv):
        if self.isRunning():return False
        self.action=name;self.argv=list(argv);return True
    def run(self):
        import subprocess
        try:
            result=subprocess.run(self.argv,capture_output=True,text=True,timeout=240,
                    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},check=False)
            details=(result.stdout+'\n'+result.stderr)[-24000:]
            self.complete.emit(self.action,details,result.returncode==0)
        except (OSError,subprocess.TimeoutExpired) as exc:
            self.complete.emit(self.action,str(exc),False)


class Orbital(QWidget):
    def __init__(self,assets):
        super().__init__()
        self.setWindowTitle('Orbital — BCI Control Plane (PyQt6)')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.Window)
        self.setMinimumSize(1100,650)
        self.resize(W,H)
        self.globe=QPixmap(str(assets/'orbital-globe-exact.png'))
        if self.globe.isNull():raise RuntimeError('Original BCI Orbital globe asset missing')
        self.tab='Dashboard';self.info={};self.buttons=[]
        self.last_cpu=None;self.last_net=None;self.cpu_pct=None
        self.rx_mbps=None;self.tx_mbps=None;self.traffic=[]
        self.last_update='Not sampled';self.drag_pos=None;self.pressed=None
        self._closing=False
        # The Poller is owned by the window throughout its lifetime.
        # Keep the thread alive while refresh inspects its running state.
        self.poller=Poller(self)
        self.poller.collected.connect(self.accept_snapshot)
        self.poller.finished.connect(self._finish_pending_close)
        self.operator=Operation(self)
        self.operator.complete.connect(self.operation_complete)
        self.operator.finished.connect(self._finish_pending_close)
        self.actions={
          'System Status':self.show_status,'Verify Evidence':self.verify_evidence,
          'Neural Status':self.show_neural,'Services':self.show_services,
          'Generate Report':self.generate_report,'Policy & Control':self.show_policy,
          'Train Status':self.show_training,'Prepare':self.training_prepare,
          'Review':self.training_review,'Run':self.training_run,
          'Evaluate':self.training_evaluate,'Promote':self.training_gate,
          'Rollback':self.training_gate,'View All':self.show_logs,
          'View Logs':self.show_logs,'Refresh':self.refresh,
          'Host Logs':lambda:self.show_logs('host'),
          'Neural Logs':lambda:self.show_logs('neural'),
          'Packet Logs':lambda:self.show_logs('packet'),
          'AI Model':lambda:self.ask_ai('model status'),
          'AI Anomalies':lambda:self.ask_ai('show anomalies'),
          'AI Context':lambda:self.ask_ai('network context'),
          'AI Baselines':lambda:self.ask_ai('what are your baselines'),
          'AI Training':lambda:self.ask_ai('training readiness'),
          'Score Dataset':self.ai_score_dataset,
          'Import Model':self.ai_import_help,
        }
        # Native conversation widgets. No remote AI endpoints, no shell/prompt execution.
        self.chat_view=QPlainTextEdit(self)
        self.chat_view.setObjectName('orbitalAiTranscript')
        self.chat_view.setAccessibleName('Orbital AI conversation')
        self.chat_view.setReadOnly(True)
        self.chat_view.setStyleSheet('QPlainTextEdit{background:#071A2C;color:#E3F5FE;border:1px solid #276386;'
                                   'border-radius:10px;padding:15px;font:16px "Rajdhani";}')
        self.chat_view.setPlainText('ORBITAL AI  |  BEACON COMPUTING INITIATIVE\n'
                                    'Developer Seal: CJB-DEV-2026\n\n'
                                    'I use the original trained Orbital neural checkpoint for anomaly interpretation. '
                                    'My language interface is a fixed command router, not an LLM.\n'
                                    'Ask "help", "what are your baselines?", or "what anomalies did you find?"\n')
        self.chat_input=QLineEdit(self)
        self.chat_input.setObjectName('orbitalAiInput')
        self.chat_input.setAccessibleName('Ask Orbital AI a question')
        self.chat_input.setMaxLength(1200)
        self.chat_input.setPlaceholderText('Ask Orbital about anomalies, context, model, or evidence…')
        self.chat_input.setStyleSheet('QLineEdit{background:#0A2841;color:white;border:1px solid #2288AA;'
                                      'border-radius:7px;padding:10px;font:17px "Rajdhani";}')
        self.chat_input.returnPressed.connect(self.send_ai_message)
        self.chat_send=QPushButton('SEND',self)
        self.chat_send.setObjectName('orbitalAiSend')
        self.chat_send.setAccessibleName('Send message to Orbital AI')
        self.chat_send.setStyleSheet('QPushButton{background:#064F79;color:white;border:1px solid #00E5FF;'
                                     'border-radius:7px;font:bold 17px "Rajdhani";} '
                                     'QPushButton:hover{background:#087BA4;}')
        self.chat_send.clicked.connect(self.send_ai_message)
        self.chat_view.hide();self.chat_input.hide();self.chat_send.hide()
        self.position_ai_widgets()
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(12000)
        QShortcut(QKeySequence('Ctrl+R'),self,activated=self.refresh)
        QShortcut(QKeySequence('Ctrl+Q'),self,activated=self.close)
        for i in range(10):
            # Alt+1 ... Alt+9, Alt+0 navigates all pages
            k=str((i+1)%10)
            QShortcut(QKeySequence('Alt+'+k),self,activated=lambda i=i:self.navigate(TABS[i]))
        QShortcut(QKeySequence('Ctrl+Alt+A'),self,activated=lambda:self.navigate('Orbital AI'))
        QTimer.singleShot(0,self.refresh)

    def _finish_pending_close(self):
        # QThread wrappers remain owned by this window, never deleteLater'ed.
        if self._closing and not self.poller.isRunning() and not self.operator.isRunning():
            QTimer.singleShot(0,self.close)

    def closeEvent(self,event):
        self.timer.stop()
        running=[w for w in (self.poller,self.operator) if w.isRunning()]
        if running:
            self._closing=True
            for worker in running:
                worker.requestInterruption()
            # Closing occurs IF AND ONLY IF both native threads have finished.
            # In-flight neural operations have a bounded subprocess timeout.
            event.ignore()
            return
        event.accept()

    def refresh(self):
        if self._closing or self.poller.isRunning():return
        self.poller.start()

    def accept_snapshot(self,data):
        if self._closing:return
        if 'error' in data:
            self.info={'states':{'host':'unknown','packet':'unknown','neural':'unknown'},
                       'services_up':0,'journal_valid':False,'error':data['error'],
                       'events':[]}
            self.last_update='Error';self.update();return
        ts=time.time()
        cpu=data.get('cpu_counters')
        if cpu and self.last_cpu:
            dt=cpu[0]-self.last_cpu[0];idle=cpu[1]-self.last_cpu[1]
            if dt>0:self.cpu_pct=max(0,min(100,round(100*(1-idle/dt))))
        self.last_cpu=cpu
        iface=data.get('current_interface','unknown')
        nb=net_bytes(iface)
        self.rx_mbps=None
        self.tx_mbps=None
        if nb is not None:
            if self.last_net and self.last_net[0]==iface:
                elapsed=ts-self.last_net[1]
                rx_delta=nb[0]-self.last_net[2]
                tx_delta=nb[1]-self.last_net[3]
                if elapsed>0 and rx_delta>=0 and tx_delta>=0:
                    self.rx_mbps=rx_delta*8/(elapsed*1e6)
                    self.tx_mbps=tx_delta*8/(elapsed*1e6)
            self.last_net=(iface,ts,nb[0],nb[1])
        else:
            self.last_net=None
        # A missing sensor sample is a gap, never a fabricated zero.
        self.traffic.append((ts,self.rx_mbps,self.tx_mbps))
        self.traffic=[r for r in self.traffic if ts-r[0]<=300][-100:]
        self.info=data
        self.last_update=datetime.now().strftime('%H:%M:%S')
        self.update()

    def navigate(self,label):
        if label in TABS:
            self.tab=label
            visible=(label=='Orbital AI')
            self.chat_view.setVisible(visible)
            self.chat_input.setVisible(visible)
            self.chat_send.setVisible(visible)
            self.position_ai_widgets()
            self.update()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'chat_view'):
            self.position_ai_widgets()

    def position_ai_widgets(self):
        if not hasattr(self,'chat_view'):return
        scale,offx,offy=self.scale_transform()
        def place(widget,x,y,w,h):
            widget.setGeometry(round(offx+x*scale),round(offy+y*scale),
                               max(20,round(w*scale)),max(20,round(h*scale)))
        place(self.chat_view,309,328,884,423)
        place(self.chat_input,309,766,747,52)
        place(self.chat_send,1072,766,121,52)

    def ask_ai(self,prompt):
        self.navigate('Orbital AI')
        self.chat_input.setText(prompt)
        self.send_ai_message()

    def send_ai_message(self):
        msg=self.chat_input.text().strip()
        if not msg:return
        self.chat_input.clear()
        try: reply=ai_respond(msg,self.info)
        except Exception as exc:
            reply='HOLD: Orbital evidence query failed: '+type(exc).__name__
        self.chat_view.appendPlainText('\nYOU > '+msg+'\n\nORBITAL > '+reply+'\n')
        sb=self.chat_view.verticalScrollBar();sb.setValue(sb.maximum())
        self.update()

    def ai_import_help(self):
        self.dialog('Import Original Neural Model',
           'The original Chance-account model and historical scores are not included in the GUI release.\n\n'
           'Use the dedicated checksum-verified import step from a BCI terminal:\n'
           'bash scripts/import-trained-model.sh\n\n'
           'Only the exact v0.2.0 trained checkpoint and matching scored report will be accepted. '
           'No retraining, model promotion, or containment occurs.')

    def ai_score_dataset(self):
        model=ai_model_state()
        if not model['available']:
            self.ai_import_help();return
        path,_=QFileDialog.getOpenFileName(self,'Select VERIFIED matching-context neural candidate',
                                           str(HOME),'JSONL (*.jsonl)')
        if not path:return
        try:argv=ai_score_argv(path)
        except (OSError,ValueError) as exc:
            self.dialog('Native Neural Scoring HOLD',str(exc));return
        self.start_operation('Original Orbital neural scoring',argv,
            'Invoke the original 12→8→3→8→12 neural scorer on this hash-verified candidate?\n'
            'The native scorer rejects context mismatches; no service or response is modified.')


    def scale_transform(self):
        scale=min(self.width()/W,self.height()/H)
        return scale,(self.width()-W*scale)/2,(self.height()-H*scale)/2

    def local(self,pos):
        s,x,y=self.scale_transform()
        return ((pos.x()-x)/s,(pos.y()-y)/s)

    def make_font(self,size=15,bold=False,mono=False):
        font=QFont('JetBrains Mono' if mono else 'Rajdhani')
        font.setPixelSize(size)
        font.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
        return font

    def text(self,p,txt,x,y,w=300,h=32,size=16,color=WHITE,bold=False,align=None,mono=False):
        p.setPen(color);p.setFont(self.make_font(size,bold,mono))
        p.drawText(QRectF(x,y,w,h),Qt.AlignmentFlag.AlignVCenter|
                (align or Qt.AlignmentFlag.AlignLeft),str(txt))

    def panel(self,p,x,y,w,h,accent=None,rounding=11):
        grad=QLinearGradient(x,y,x+w,y+h)
        grad.setColorAt(0,QColor('#122B42'))
        grad.setColorAt(.45,QColor('#0B1A2C'))
        grad.setColorAt(1,QColor('#071624'))
        p.setBrush(QBrush(grad));p.setPen(QPen(accent or QColor('#315570'),1.4))
        p.drawRoundedRect(QRectF(x,y,w,h),rounding,rounding)

    def button(self,p,label,x,y,w,h,primary=False,locked=False):
        self.buttons.append((label,QRectF(x,y,w,h)))
        grad=QLinearGradient(x,y,x,y+h)
        grad.setColorAt(0,QColor('#174F7A') if primary else QColor('#1D354B'))
        grad.setColorAt(1,QColor('#062D51') if primary else QColor('#102336'))
        p.setBrush(QBrush(QColor('#172639')) if locked else QBrush(grad))
        p.setPen(QPen(QColor('#365063') if locked else (CYAN if primary else QColor('#4A7190')),1.3))
        p.drawRoundedRect(QRectF(x,y,w,h),6,6)
        self.text(p,label,x,y,w,h,15 if w<140 else 17,
                  QColor('#819CAF') if locked else WHITE,True,Qt.AlignmentFlag.AlignHCenter)

    def status_badge(self,p,x,y,state):
        good=state=='active';color=GREEN if good else RED if state in ('failed','quota_hold','restart_limit') else MUTED
        p.setBrush(QColor('#07382C') if good else QColor('#15293C'))
        p.setPen(QPen(color,1.2));p.drawRoundedRect(QRectF(x,y,84,27),5,5)
        label='QUOTA HOLD' if state=='quota_hold' else 'RESTART HOLD' if state=='restart_limit' else 'ACTIVE' if good else str(state).upper()
        self.text(p,label,x,y,84,27,11 if len(label)>7 else 13,color,True,Qt.AlignmentFlag.AlignHCenter)

    def draw_shell(self,p):
        p.fillRect(QRectF(0,0,W,H),QColor('#05080D'))
        p.setPen(QPen(QColor('#2D5877'),1))
        p.setBrush(QColor('#102236'));p.drawRect(QRectF(0,0,W,40))
        self.text(p,'◉  Orbital — BCI Control Plane (PyQt6)',18,1,460,38,17,WHITE)
        for label,x in [('—',1503),('▢',1569),('×',1628)]:
            self.text(p,label,x,0,44,39,25,WHITE,False,Qt.AlignmentFlag.AlignHCenter)
            self.buttons.append(({'—':'MIN','▢':'MAX','×':'CLOSE'}[label],QRectF(x,0,44,40)))
        p.setBrush(QColor('#071320'));p.setPen(QPen(QColor('#21435B'),1))
        p.drawRect(QRectF(0,41,W,86))
        p.setPen(QPen(CYAN,4))
        p.drawEllipse(QRectF(27,59,75,48))
        p.drawEllipse(QRectF(33,48,63,70))
        self.text(p,'BCI Orbital',128,50,320,33,34,WHITE,True)
        self.text(p,'BEACON COMPUTING INITIATIVE',128,82,315,23,16,CYAN,True)
        self.text(p,'Cyber Defense Control Plane',128,103,315,18,14,MUTED)
        p.setPen(QPen(QColor('#325876'),1));p.drawLine(451,52,451,117)
        self.text(p,'Unified Monitoring  •  Neural Intelligence  •  Evidence Correlation  •  Controlled Response',480,68,815,42,18,WHITE)
        self.panel(p,1350,58,279,54)
        self.text(p,'◇   Developer Seal: CJB-DEV-2026',1361,65,260,40,15,WHITE)
        # Sidebar is redrawn natively. Original luminous Earth image is preserved
        # pixel-for-pixel, unscaled at the 1672x941 reference viewport.
        p.setPen(QPen(QColor('#224862'),1));p.setBrush(QColor('#07121E'))
        p.drawRect(QRectF(0,127,247,747))
        p.drawPixmap(QRectF(0,618,247,195),self.globe,QRectF(0,0,self.globe.width(),self.globe.height()))
        self.text(p,'Orbital v'+VERSION,19,809,214,28,20,WHITE,True)
        self.text(p,'BCI Control Plane (PyQt6)',19,835,224,24,15,MUTED)
        for i,name in enumerate(TABS):
            y=151+i*42
            active=self.tab==name
            if active:
                p.setPen(QPen(CYAN,1.8));p.setBrush(QColor('#075283'))
            else:
                p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor('#071725'))
            p.drawRoundedRect(QRectF(12,y,223,43),8,8)
            self.text(p,GLYPHS[i],26,y+2,31,37,23,CYAN if active else MUTED,True)
            self.text(p,name,75,y+2,150,37,20,WHITE,active)
            self.buttons.append((name,QRectF(12,y,223,43)))
        # Main page header
        self.text(p,'Orbital Dashboard' if self.tab=='Dashboard' else self.tab,313,142,780,40,32,WHITE,True)
        self.text(p,'Live system status, activity, and neural readiness' if self.tab=='Dashboard'
                  else 'BEACON COMPUTING INITIATIVE  •  ORBITAL CONTROL PLANE',315,179,800,25,17,CYAN if self.tab!='Dashboard' else MUTED)
        now=datetime.now().strftime('%a, %b %d, %Y   %H:%M:%S')
        self.text(p,now,1270,145,355,25,16,WHITE,True,Qt.AlignmentFlag.AlignRight)
        ctx=short(self.info.get('current_context','unavailable'),28)
        host=short(self.info.get('hostname','—'),20)
        self.text(p,f'Host: {host}  |  Context: {ctx}',1125,175,500,25,13,MUTED,False,Qt.AlignmentFlag.AlignRight)

    def progress(self,p,label,n,target,x,y,w):
        self.text(p,label,x,y,w-100,25,15,WHITE)
        self.text(p,f'{n:g} / {target:g}',x+w-97,y,95,25,14,MUTED,True,Qt.AlignmentFlag.AlignRight)
        p.setBrush(QColor('#092237'));p.setPen(QPen(QColor('#32516B'),1))
        p.drawRoundedRect(QRectF(x,y+30,w,9),4,4)
        if n>0:
            p.setBrush(GREEN);p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(QRectF(x+1,y+31,max(3,(w-2)*min(1,n/target)),7),3,3)

    def draw_chart(self,p):
        self.panel(p,261,309,572,241)
        self.text(p,'Live Activity (Last 5 Minutes)',278,314,500,32,20,WHITE,True)
        p.setPen(QPen(QColor('#31526B'),1));p.drawLine(261,346,833,346)
        left,top,cw,ch=357,370,450,139
        p.setPen(QPen(QColor('#29475C'),.9))
        for i in range(5):p.drawLine(left,int(top+i*ch/4),left+cw,int(top+i*ch/4))
        for i in range(6):p.drawLine(int(left+i*cw/5),top,int(left+i*cw/5),top+ch)
        pts=self.traffic
        peak=max((v for r in pts for v in r[1:] if v is not None),default=.5)
        peak=max(.5,math.ceil(peak*2)/2)
        for i in range(5):
            self.text(p,f'{peak*(4-i)/4:.1f}',295,top-12+i*ch/4,52,23,12,MUTED,False,Qt.AlignmentFlag.AlignRight)
        if len(pts)>1:
            t0=max(pts[0][0],pts[-1][0]-300);t1=max(t0+1,pts[-1][0])
            for idx,color in ((1,CYAN),(2,PURPLE)):
                p.setPen(QPen(color,2.2))
                prior=None
                for r in pts:
                    if r[0]<t0 or r[idx] is None:
                        prior=None
                        continue
                    point=QPointF(left+cw*(r[0]-t0)/(t1-t0),top+ch*(1-min(1,r[idx]/peak)))
                    if prior is not None:p.drawLine(prior,point)
                    prior=point
        if not any(r[1] is not None or r[2] is not None for r in pts):
            self.text(p,'Waiting for valid interface samples…',428,421,360,37,16,MUTED)
        self.text(p,'5m ago',357,509,95,24,13,MUTED)
        self.text(p,'now',741,509,66,24,13,MUTED,False,Qt.AlignmentFlag.AlignRight)
        p.setPen(QPen(CYAN,3));p.drawLine(417,532,441,532)
        self.text(p,'Inbound (Mb/s)',446,520,160,24,13,MUTED)
        p.setPen(QPen(PURPLE,3));p.drawLine(614,532,638,532)
        self.text(p,'Outbound (Mb/s)',645,520,160,24,13,MUTED)

    def draw_metrics(self,p):
        self.panel(p,845,309,329,241)
        self.text(p,'System Metrics',858,315,265,30,20,WHITE,True)
        p.setPen(QPen(QColor('#31526B'),1));p.drawLine(846,346,1173,346)
        for i,(label,val) in enumerate([('CPU',self.cpu_pct),('Memory',self.info.get('mem_pct')),
                                       ('Disk',self.info.get('disk_pct'))]):
            y=352+i*40
            self.text(p,label,881,y,170,23,17,WHITE,True)
            self.text(p,'—' if val is None else f'{val}%',1081,y,66,23,17,WHITE,True,Qt.AlignmentFlag.AlignRight)
            p.setBrush(QColor('#0A2136'));p.setPen(QPen(QColor('#35516A'),1))
            p.drawRoundedRect(QRectF(920,y+27,225,9),4,4)
            if val is not None:
                p.setPen(Qt.PenStyle.NoPen);p.setBrush(GREEN if i>0 else CYAN)
                p.drawRoundedRect(QRectF(920,y+28,max(3,223*val/100),7),3,3)
        self.text(p,'Network ('+str(self.info.get('current_interface','unknown'))+')',880,474,268,30,17,WHITE,True)
        self.text(p,'↓ — Mb/s' if self.rx_mbps is None else f'↓ {self.rx_mbps:.2f} Mb/s',877,509,148,25,16,GREEN,True)
        self.text(p,'↑ — Mb/s' if self.tx_mbps is None else f'↑ {self.tx_mbps:.2f} Mb/s',1030,509,138,25,16,PURPLE,True)

    def draw_training(self,p):
        self.panel(p,1187,217,446,401)
        self.text(p,'◇  Neural Training',1206,230,389,36,22,WHITE,True)
        ready=verified_preparation_status(self.info)
        p.setBrush(QColor('#073729'));p.setPen(QPen(GREEN,1.1))
        p.drawRoundedRect(QRectF(1201,274,417,64),8,8)
        self.text(p,'◷  Training Readiness',1215,278,390,29,19,GREEN,True)
        label='ELIGIBLE FOR DATASET REVIEW' if ready['qualified_for_review'] else 'WAIT: 7 DAYS  /  24 HOURS  /  80 WINDOWS'
        self.text(p,label,1214,307,388,25,13,WHITE,True,Qt.AlignmentFlag.AlignHCenter)
        self.progress(p,'Observation Windows',ready['windows'],80,1208,347,408)
        self.progress(p,'Distinct Observation Hours',ready['hours'],24,1208,400,408)
        self.progress(p,'Elapsed Training Days',ready['days'],7,1208,453,408)
        self.button(p,'Train Status',1201,516,139,44,primary=True)
        self.button(p,'Prepare',1348,516,134,44,locked=not ready['qualified_for_review'])
        self.button(p,'Review',1490,516,134,44)
        for label,x,w in (('Run',1201,96),('Evaluate',1305,102),('Promote',1415,101),('Rollback',1524,100)):
            self.button(p,label,x,568,w,39,locked=label in ('Promote','Rollback'))

    def mini_card(self,p,x,title,value,detail,color=CYAN):
        self.panel(p,x,558,222,94)
        self.text(p,title,x+16,565,200,25,17,WHITE,True)
        self.text(p,short(value,18),x+16,592,200,32,24,color,True)
        self.text(p,detail,x+16,626,202,17,12,MUTED)

    def draw_service_cards(self,p):
        states=self.info.get('states',{})
        for x,w,name,key,desc in ((261,300,'Host Monitor','host','Process / socket / USB'),
                                   (573,300,'Packet Collector','packet','Route-aware SHA-256 + DNS'),
                                   (885,289,'Neural Collector','neural','Rate-aware feature collection')):
            self.panel(p,x,218,w,79)
            self.text(p,name,x+16,224,w-112,30,19,WHITE,True)
            self.text(p,desc,x+16,261,w-25,22,13,MUTED)
            self.status_badge(p,x+w-99,228,(self.info.get('packet_condition','unknown') if key=='packet' else states.get(key,'unknown')))
        packet=self.info.get('packet_condition',states.get('packet','unknown'))
        self.mini_card(p,261,'Packet Evidence','ACTIVE' if packet=='active' else packet.upper(),'Service state; verify chain',GREEN if packet=='active' else RED)
        self.mini_card(p,490,'Neural Windows',str(self.info.get('neural_window_count',0)),'Live unreviewed samples')
        context=str(self.info.get('current_context','unavailable'))
        self.mini_card(p,719,'Current Context',short(context,16),'Host / route scope')
        self.mini_card(p,948,'Model Status','HOLD','No live inference',MUTED)

    def draw_events(self,p):
        self.panel(p,261,665,912,190)
        self.text(p,'Recent Events',278,669,620,34,20,WHITE,True)
        self.button(p,'View All',1090,672,77,29)
        p.setPen(QPen(QColor('#35556B'),1));p.drawLine(262,706,1171,706)
        ev=self.info.get('events',[])[:5]
        if not ev:ev=[{'time':'—','label':'No accessible recent events (open Logs for diagnostics)'}]
        for i,e in enumerate(ev):
            y=709+i*28
            p.setPen(Qt.PenStyle.NoPen);p.setBrush(GREEN)
            p.drawEllipse(QRectF(286,y+7,13,13))
            self.text(p,'✓',286,y+5,13,16,11,QColor('#002F26'),True,Qt.AlignmentFlag.AlignHCenter)
            self.text(p,short(e.get('time','—')[-14:],16),314,y,165,24,13,MUTED)
            self.text(p,short(e.get('label',''),85),485,y,670,24,15,WHITE)
            p.setPen(QPen(QColor('#244359'),.7));p.drawLine(310,y+27,1155,y+27)

    def draw_control_actions(self,p):
        self.panel(p,1187,630,446,225)
        self.text(p,'⚙  Control Plane Actions',1204,637,402,31,20,WHITE,True)
        buttons=[('System Status',1204,683),('Verify Evidence',1345,683),('Neural Status',1486,683),
                 ('Services',1204,761),('Generate Report',1345,761),('Policy & Control',1486,761)]
        for name,x,y in buttons:self.button(p,name,x,y,131,68)

    def draw_dashboard(self,p):
        self.draw_service_cards(p)
        self.draw_chart(p)
        self.draw_metrics(p)
        self.draw_training(p)
        self.draw_events(p)
        self.draw_control_actions(p)

    def kv_rows(self,p,items):
        self.panel(p,284,280,1324,467)
        for i,(key,value) in enumerate(items[:9]):
            y=296+i*51
            self.text(p,key,307,y,372,40,18,MUTED,True)
            self.text(p,short(value,108),705,y,877,40,17,WHITE,True,mono='sha' in key.lower())
            p.setPen(QPen(QColor('#294963'),1));p.drawLine(306,y+44,1585,y+44)

    def detail_cards(self,p,items):
        for i,(name,val,desc) in enumerate(items):
            x=285+(i%2)*658;y=283+(i//2)*178
            self.panel(p,x,y,627,157)
            self.text(p,name,x+25,y+14,560,35,23,WHITE,True)
            color=GREEN if val=='active' else RED if val=='failed' else CYAN
            self.text(p,short(val,38).upper(),x+25,y+57,554,43,27,color,True)
            self.text(p,desc,x+25,y+108,555,28,16,MUTED)

    def draw_ai(self,p):
        self.panel(p,284,278,927,571,accent=QColor('#286C96'))
        self.text(p,'◈  Orbital Native AI  |  Neural Evidence Interface',310,284,860,32,21,WHITE,True)
        self.text(p,'Verified model outputs • Rule-based language routing • No external AI',310,305,860,23,13,CYAN)
        self.panel(p,1222,278,385,571)
        self.text(p,'◈   Neural Core Binding',1239,291,344,35,22,WHITE,True)
        state=ai_model_state()
        color=GREEN if state.get('available') else RED
        self.text(p,'MODEL VERIFIED' if state.get('available') else 'MODEL IMPORT REQUIRED',1240,341,352,35,20,color,True)
        self.text(p,'Original 12 → 8 → 3 → 8 → 12',1242,380,330,25,17,WHITE)
        self.text(p,'Legacy checkpoint • unpromoted',1242,407,340,24,15,MUTED)
        self.text(p,'Live scoring: HOLD (context mismatch)',1242,440,351,27,15,RED)
        self.text(p,'No LLM, no cloud, no containment',1242,467,351,27,15,MUTED)
        for name,y in [('AI Model',516),('AI Anomalies',571),('AI Context',626),('AI Baselines',681)]:
            self.button(p,name,1240,y,165,42,primary=(name=='AI Anomalies'))
        self.button(p,'Import Model',1415,516,174,42,locked=state.get('available',False))
        self.button(p,'Score Dataset',1415,572,174,42,locked=not state.get('available',False))
        self.button(p,'AI Training',1415,700,174,42)
        self.text(p,'Hash-verified datasets only.',1416,624,176,23,12,MUTED)
        self.text(p,'Legacy context must match.',1416,645,176,23,12,MUTED)
        self.text(p,'No automated promotion.',1416,666,180,23,12,MUTED)
        self.text(p,'Evidence is interpreted, not invented.',1243,766,334,32,14,CYAN)

    def draw_detail(self,p):
        p.setPen(QPen(QColor('#31526B'),1));p.drawLine(283,264,1606,264)
        d=self.info;states=d.get('states',{});j=d.get('journal',{});neural=d.get('neural_status') or {}
        if self.tab=='Sensors':
            self.detail_cards(p,[('Host Monitor',states.get('host','unknown'),'Processes, sockets and USB'),
                ('Dynamic Packet/DNS',states.get('packet','unknown'),'Route-aware, root-owned; separate privilege'),
                ('Neural Timer',states.get('neural','unknown'),'Five-minute rate-aware candidate capture'),
                ('Active Network',d.get('current_interface','unknown'),'Default outbound interface')])
        elif self.tab=='Context':
            self.kv_rows(p,[('Host',d.get('hostname','unavailable')),
                ('Live context',d.get('current_context','unavailable')),
                ('Host fingerprint',d.get('host_id','unavailable')),
                ('Route fingerprint',d.get('route_id','unavailable')),
                ('Interface',d.get('current_interface','unknown')),
                ('Trust','Unreviewed live telemetry'),
                ('Legacy context','Not automatically mapped to current BCI context')])
        elif self.tab=='Evidence':
            self.kv_rows(p,[('Rate-aware journal',str(JOURNAL)),
                ('Journal chain','VALID' if j.get('valid') else 'NOT VERIFIED'),
                ('Journal entries',str(j.get('count',0))),
                ('Head SHA-256',j.get('head','unavailable')),
                ('Packet evidence','Verify explicitly using polkit'),
                ('Independent anchor','Not configured'),
                ('SHA-256 reports',str(HOME/'.local/state/bci-orbital-gui/reports'))])
        elif self.tab=='Neural Core':
            self.kv_rows(p,[('Architecture','12 → 8 → 3 → 8 → 12 autoencoder'),
                ('Neural mode',neural.get('neural_core','experimental / isolated')),
                ('Current windows',str(d.get('neural_window_count',0))),
                ('Candidate journal integrity','PASS' if d.get('journal_valid') else 'HOLD'),
                ('Live scoring','NOT ENABLED'),('Training','REQUIRES REVIEW'),
                ('Legacy model','Unpromoted; context incompatible'),
                ('Automatic containment','DISABLED')])
        elif self.tab=='Training':
            st=verified_preparation_status(d)
            self.kv_rows(p,[('Observation windows',f"{st['windows']} / 80"),
                ('Distinct hours',f"{st['hours']} / 24"),
                ('Elapsed days',f"{st['days']} / 7"),
                ('Current context',str(st['context'])),
                ('Live interface match',str(st['interface_matches'])),
                ('Fresh sample',str(st['last_window_fresh'])),
                ('Eligible for review',str(st['qualified_for_review'])),
                ('Training approval','REQUIRED; not baseline approval')])
        elif self.tab=='Alerts':
            self.kv_rows(p,[('Source','Host monitor journal'),
                ('Rule alerts','Use View Logs for exact classification'),
                ('Neural anomalies','Not enabled on live system'),
                ('Sensor visibility','Gaps are not proof of compromise'),
                ('Containment','DISABLED')])
        elif self.tab=='Control Plane':
            self.kv_rows(p,[('Host service',states.get('host','unknown')),
                ('Packet service',states.get('packet','unknown')),
                ('Neural timer',states.get('neural','unknown')),
                ('Control mode','Read-only health / reports; gated candidate operations'),
                ('Packet privilege','Root-owned isolated service'),
                ('Training authorization','EXPLICIT, VERIFIED DATASET ONLY'),
                ('Firewall response','DISABLED')])
        elif self.tab=='Reports':
            self.kv_rows(p,[('Format','JSON + SHA-256 sidecar'),
                ('Storage',str(HOME/'.local/state/bci-orbital-gui/reports')),
                ('Identity',HEADER+'  |  '+SEAL),
                ('Action','Generate Report creates a new file (never overwrites)')])
        else:
            self.kv_rows(p,[('GUI version','0.8.0'),('Original globe','Exact approved mockup pixels'),
                ('Rendering','Native single-layer PyQt6 components'),
                ('Refresh interval','12 seconds, persistent QThread worker'),
                ('Hotkeys','Alt+1 ... Alt+0; Ctrl+R; Ctrl+Q'),
                ('Privilege policy','GUI unprivileged; polkit optional'),
                ('Developer seal',SEAL)])
        self.button(p,'Refresh',288,777,163,51,primary=True)
        self.button(p,'Generate Report',467,777,210,51)
        self.button(p,'View Logs',692,777,161,51)
        if self.tab=='Training':
            self.button(p,'Prepare',879,777,153,51,locked=not verified_preparation_status(d)['qualified_for_review'])
            self.button(p,'Review',1044,777,151,51)
            self.button(p,'Run',1208,777,150,51)
            self.button(p,'Evaluate',1372,777,150,51)
        if self.tab=='Sensors':
            for label,x in (('Host Logs',879),('Neural Logs',1061),('Packet Logs',1243)):
                self.button(p,label,x,777,170,51)

    def draw_footer(self,p):
        p.setPen(QPen(QColor('#2C5770'),1));p.setBrush(QColor('#091B2B'))
        p.drawRect(QRectF(0,875,1672,66))
        up=self.info.get('services_up',0)
        state='Operational' if up==3 else 'Partial / Inspect'
        color=GREEN if up==3 else RED
        p.setBrush(color);p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(21,892,17,17))
        self.text(p,'Orbital: '+state,48,885,230,34,18,color,True)
        fields=[f'Services: {up}/3 Active',
                'Journal: '+('Verified' if self.info.get('journal_valid') else 'Check'),
                'Model: Unpromoted','Training: Gated','Inference: Disabled','Containment: Disabled']
        for i,f in enumerate(fields):self.text(p,f,283+i*195,886,198,31,13,MUTED)
        self.text(p,'Updated '+self.last_update,1462,885,182,35,13,GREEN,True,Qt.AlignmentFlag.AlignRight)

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        s,x,y=self.scale_transform();painter.translate(x,y);painter.scale(s,s)
        self.buttons=[]
        self.draw_shell(painter)
        if self.tab=='Dashboard':self.draw_dashboard(painter)
        elif self.tab=='Orbital AI':self.draw_ai(painter)
        else:self.draw_detail(painter)
        self.draw_footer(painter)
        if not self.info:
            self.panel(painter,578,400,520,95,accent=CYAN)
            self.text(painter,'Connecting to Orbital services…',603,419,462,54,24,WHITE,True,Qt.AlignmentFlag.AlignHCenter)
        elif self.info.get('error'):
            self.panel(painter,578,400,520,95,accent=RED)
            self.text(painter,short(self.info['error'],55),603,420,462,54,21,RED,True,Qt.AlignmentFlag.AlignHCenter)
        painter.end()

    def mousePressEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton:return
        self.pressed=None
        x,y=self.local(event.position())
        if 0<=y<=40 and x<1490:
            self.drag_pos=event.globalPosition().toPoint()-self.frameGeometry().topLeft()
            return
        for label,rect in reversed(self.buttons):
            if rect.contains(x,y):self.pressed=(label,rect);return

    def mouseMoveEvent(self,event):
        if self.drag_pos is not None:self.move(event.globalPosition().toPoint()-self.drag_pos)

    def mouseReleaseEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton:return
        if self.drag_pos is not None:self.drag_pos=None;return
        pressed=self.pressed;self.pressed=None
        if pressed is None:return
        label,rect=pressed;x,y=self.local(event.position())
        if not rect.contains(x,y):return
        if label=='CLOSE':self.close();return
        if label=='MIN':self.showMinimized();return
        if label=='MAX':self.showNormal() if self.isMaximized() else self.showMaximized();return
        if label in TABS:self.navigate(label);return
        action=self.actions.get(label)
        if action:action()

    def dialog(self,title,content):
        dlg=QDialog(self)
        dlg.setWindowTitle('BCI Orbital — '+title)
        dlg.resize(875,585)
        dlg.setStyleSheet('QDialog{background:#071320;color:#F4F8FB;} QLabel{font-size:20px;font-weight:bold;color:#00E5FF;} '
              'QPlainTextEdit{background:#0B2236;color:#ECF7FC;border:1px solid #2E607D;font:13px "JetBrains Mono";} '
              'QPushButton{background:#0B3D63;color:#F4F8FB;border:1px solid #00C5DE;padding:11px;border-radius:6px;}')
        lay=QVBoxLayout(dlg)
        lay.addWidget(QLabel(f'{HEADER}  |  {title}'))
        box=QPlainTextEdit();box.setReadOnly(True);box.setPlainText(str(content));lay.addWidget(box)
        row=QHBoxLayout()
        copy=QPushButton('Copy Details');copy.clicked.connect(lambda:QApplication.clipboard().setText(str(content)))
        done=QPushButton('Close');done.clicked.connect(dlg.accept)
        row.addWidget(copy);row.addWidget(done);lay.addLayout(row)
        dlg.exec()

    def show_status(self):self.dialog('System Status',json.dumps(self.info,indent=2,default=str))
    def show_neural(self):
        self.dialog('Neural Status',json.dumps({'status':self.info.get('neural_status'),
                     'live_rate_aware_readiness':verified_preparation_status(self.info)},indent=2))
    def show_training(self):
        self.dialog('Training Readiness',json.dumps({'header':HEADER,'developer_seal':SEAL,
            **verified_preparation_status(self.info)},indent=2))
    def show_services(self):
        self.dialog('Service Health',json.dumps({'header':HEADER,'developer_seal':SEAL,
            'services':self.info.get('states',{}),
            'details':self.info.get('service_details',{}),
            'packet_condition':self.info.get('packet_condition','unknown'),'note':'Active means service running, not that all sensors are proven complete'},indent=2))
    def show_policy(self):
        self.dialog('Policy and Containment',json.dumps({'header':HEADER,'developer_seal':SEAL,
           'mode':'operator-review / no automatic response','training_authorized':False,
           'model_promoted':False,'containment_authorized':False,
           'note':'The GUI has no method to disable safeguards or issue firewall commands'},indent=2))
    def training_gate(self):
        self.dialog('Model Registry HOLD','Model promotion and rollback require a verified model registry, independent evaluation, and a documented rollback implementation.\n\nNo model, baseline, or service was modified.')
    def training_prepare(self):
        if not verified_preparation_status(self.info)['qualified_for_review']:
            self.show_training();return
        ans=QMessageBox.question(self,'BCI — Freeze candidate',
             'Create a new unapproved training candidate from the currently verified live context?\nNo training or baseline approval occurs.',
             QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if ans!=QMessageBox.StandardButton.Yes:return
        try:result=make_candidate(self.info)
        except (Hold,OSError,ValueError) as exc:self.dialog('Dataset Preparation HOLD',str(exc));return
        self.dialog('Candidate Prepared',json.dumps(result,indent=2))

    def training_review(self):
        path,_=QFileDialog.getOpenFileName(self,'Select hashed candidate JSONL',str(HOME), 'JSONL (*.jsonl)')
        if not path:return
        ctx=self.info.get('current_context','')
        try:self.dialog('Candidate Review',review_candidate(path,ctx))
        except Hold as exc:self.dialog('Review HOLD',str(exc))

    def start_operation(self,name,argv,warning):
        if self.operator.isRunning():
            self.dialog('Operation Busy','Another neural operation is already running.');return
        answer=QMessageBox.question(self,'Orbital — '+name,warning,
                  QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if answer!=QMessageBox.StandardButton.Yes:return
        if not self.operator.configure(name,argv):return
        self.operator.start()
        self.last_action=name+' RUNNING (no containment)'
        self.update()

    def training_run(self):
        data=self.info
        if not verified_preparation_status(data)['qualified_for_review']:
            self.dialog('Training HOLD','The live dataset has not met the qualified-context, 7-day, 24-hour, and 80-window gates. No training initiated.');return
        dataset,_=QFileDialog.getOpenFileName(self,'Select approved candidate data',str(HOME), 'JSONL (*.jsonl)')
        if not dataset:return
        approval,_=QFileDialog.getOpenFileName(self,'Select operator approval JSON',str(HOME), 'JSON (*.json)')
        if not approval:return
        path=HOME/'.local/state/bci-orbital-gui/models';path.mkdir(parents=True,exist_ok=True,mode=0o700)
        dest=path/('candidate-model-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.json')
        self.start_operation('Candidate neural training',
            [str(NEURAL),'train','--input',dataset,'--context',str(data['current_context']),
             '--approval',approval,'--output',str(dest)],
            'Train an ISOLATED, UNPROMOTED candidate using the selected dataset and approval?\nThe native training CLI re-verifies dataset hashes, approval scope, and context.')

    def training_evaluate(self):
        model,_=QFileDialog.getOpenFileName(self,'Select verified candidate neural model',str(HOME),'JSON (*.json)')
        if not model:return
        dataset,_=QFileDialog.getOpenFileName(self,'Select independent evaluation JSONL',str(HOME),'JSONL (*.jsonl)')
        if not dataset:return
        root=HOME/'.local/state/bci-orbital-gui/evaluations';root.mkdir(parents=True,exist_ok=True,mode=0o700)
        dest=root/('shadow-scores-'+datetime.now().strftime('%Y%m%dT%H%M%S%f')+'.json')
        self.start_operation('Isolated candidate scoring',
            [str(NEURAL),'score','--model',model,'--input',dataset,'--output',str(dest)],
            'Score selected observations using the existing isolated model?\nThis is a statistical score, NOT precision/recall evaluation or threat confirmation.')

    def operation_complete(self,name,raw,success):
        self.dialog(name+(' — complete' if success else ' — HOLD'),
             f'{HEADER}\nDeveloper Seal: {SEAL}\nStatus: '+('PASS' if success else 'HOLD')+'\n\n'+raw)
        self.refresh()

    def show_logs(self,kind='host'):
        try:self.dialog(kind.title()+' Service Logs',service_logs(kind))
        except Hold as exc:self.dialog('Logs HOLD',str(exc))
    def verify_evidence(self):
        pieces=[HEADER,'Developer Seal: '+SEAL]
        try:pieces.append('Host evidence:\n'+host_evidence())
        except Hold as exc:pieces.append('Host evidence HOLD: '+str(exc))
        pieces.append('Rate-aware neural journal: '+('VALID' if self.info.get('journal_valid') else 'NOT VERIFIED'))
        choice=QMessageBox.question(self,'Privileged packet evidence verification',
            'Host and neural checks are complete. Also request desktop authorization (polkit) to verify the root-owned packet evidence?\nNo data is changed.',
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if choice==QMessageBox.StandardButton.Yes:
            try:pieces.append('Packet evidence:\n'+packet_evidence_with_polkit())
            except Hold as exc:pieces.append('Packet evidence HOLD: '+str(exc))
        else:pieces.append('Packet evidence: NOT REQUESTED')
        self.dialog('Evidence Integrity','\n\n'.join(pieces))

    def generate_report(self):
        try:dest,digest=write_operator_report(HOME/'.local/state/bci-orbital-gui/reports',self.info)
        except (OSError,ValueError) as exc:self.dialog('Report HOLD',str(exc));return
        self.dialog('Report Saved',f'{HEADER}\nDeveloper Seal: {SEAL}\n{dest}\nSHA-256: {digest}\nSidecar: {dest}.sha256')


def launch(start_tab='Dashboard'):
    app=QApplication(sys.argv)
    app.setApplicationName('BCI Orbital')
    assets=Path(__file__).resolve().parent.parent/'assets'
    gui=Orbital(assets);gui.navigate(start_tab);gui.show()
    return app.exec()

if __name__=='__main__':sys.exit(launch())
