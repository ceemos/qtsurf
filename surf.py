from PyQt5.QtWebKitWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys

app = QApplication(sys.argv)
view = QWebView()

MOD = Qt.ControlModifier
always = lambda e: True

bindings = [[MOD, Qt.Key_Left		, always, view.back		],
				[MOD, Qt.Key_Right	, always, view.forward	],
				]



evmap = dict()
evmap[QEvent.TabletPress] = QEvent.MouseButtonPress
evmap[QEvent.TabletRelease] = QEvent.MouseButtonRelease
evmap[QEvent.TabletMove] = QEvent.MouseMove


class Scroller(QObject):
	def __init__(self, view):
		super(QObject, self).__init__()
		self.view = view
	
	def eventFilter(self, target, event):
		if event.type() == QEvent.ScrollPrepare:
			p = self.view.page()
			f = p.frameAt(event.startPos().toPoint())
			self.f = f
			pos = QPointF(f.scrollBarValue(1), f.scrollBarValue(0))
			rang = QRectF(QPointF(0,0), QPointF(f.scrollBarMaximum(1), f.scrollBarMaximum(0)))
			event.setContentPos(pos)
			event.setContentPosRange(rang)
			event.setViewportSize(QSizeF(p.viewportSize()))
			event.setAccepted(True)
			self.ev = event
			return True
		if event.type() == QEvent.Scroll:
			self.f.setScrollBarValue(0, event.contentPos().y())
			self.f.setScrollBarValue(1, event.contentPos().x())
			return True
		return False


class Filter(QObject):
	def __init__(self, dest):
		super(QObject, self).__init__()
		self.dest = dest
		
	def eventFilter(self, target, event):
		if event.type() in evmap:
			if event.pressure() == 0.0: # this seems to be a touch screen -- Qt tablet handling is broken
				mouseev = QMouseEvent(evmap[event.type()], QPointF(event.pos()), Qt.MidButton, Qt.MidButton, Qt.NoModifier)
				self.deadspot = event.pos()
				QCoreApplication.postEvent(self.dest, mouseev, 0)
				return True
		return False
		
class KeyHandler(QObject):
	def eventFilter(self, target, event):
		self.ev = event
		if event.type() == QEvent.KeyPress:
			for bind in bindings:
				if bind[0] == event.modifiers() \
					and bind[1] == event.key() \
					and bind[2](event):
						bind[3]()
						return True
		return False

scrolldummy = QWidget()
s = Scroller(view)
f = Filter(scrolldummy)
k = KeyHandler()
view.installEventFilter(f)
scrolldummy.installEventFilter(s)
view.installEventFilter(k)

#view.setAttribute(Qt.WA_AcceptTouchEvents)
QScroller.grabGesture(scrolldummy, QScroller.MiddleMouseButtonGesture)

view.load(QUrl("http://google.com"))
view.show()

sys.exit(app.exec_())
