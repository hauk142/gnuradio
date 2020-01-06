import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QTreeView, QAbstractItemView, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QSize, QDataStream, QVariant, Qt, QRectF
from PyQt5.QtGui import QStandardItem, QStandardItemModel
import six
import time

WINDOW_SIZE = 840, 600

# Main Canvas
class MyQGraphicsScene(QGraphicsScene):
    def __init__(self, platform):
        QGraphicsScene.__init__(self)
        self.platform = platform
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()    

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
            
    def decode_data(self, bytearray):
        data = []
        item = {}
        ds = QDataStream(bytearray)
        while not ds.atEnd():
            row = ds.readInt32()
            column = ds.readInt32()
            map_items = ds.readInt32()
            for i in range(map_items):
                key = ds.readInt32()
                value = QVariant()
                ds >> value
                item[Qt.ItemDataRole(key)] = value
            data.append(item)
        return data
                    
    def dropEvent(self, event):
        QGraphicsScene.dropEvent(self, event)
        if event.mimeData().hasUrls:
            data = event.mimeData()
            if data.hasFormat('application/x-qabstractitemmodeldatalist'):
                bytearray = data.data('application/x-qabstractitemmodeldatalist')
                data_items = self.decode_data(bytearray)

                # Pull out label text and use it to find block's key
                label_text = data_items[0][Qt.DisplayRole].value() # Assuming that we get at least one item, and that it defines text that we can display.
                # Pretty inefficient way of doing it, but on Marc's computer it takes less than 1ms, and we can always improve it later
                for block in six.itervalues(self.platform.blocks):
                    if block.label == label_text:
                        break
                print(block.key)
                
                
                event.setDropAction(QtCore.Qt.CopyAction)
                event.accept()
            else:
                return QStandardItemModel.dropMimeData(self, data, action, row, column, parent)
        else:
            event.ignore()


class MyWindow(QMainWindow):
    def __init__(self, platform):
        QMainWindow.__init__(self)

        self.platform = platform

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("Hello world - pythonprogramminglanguage.com")

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        # Set up layout
        gridLayout = QGridLayout(centralWidget)
        centralWidget.setLayout(gridLayout)        
        
        # Create QStandardItemModel to represent blocks that will show up in the TreeView
        block_model = QStandardItemModel()

        # TreeView
        self.tree = QTreeView(self)
        self.tree.setModel(block_model)
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(True) # needed to be able to click and hold on one of the rows
        self.tree.setDragDropMode(QAbstractItemView.DragOnly)
        gridLayout.addWidget(self.tree, 0, 1)
        
        # Main Canvas
        self.view = QGraphicsView()
        self.scene = MyQGraphicsScene(self.platform)
        self.scene.acceptDrops = True
        self.scene.setSceneRect(QRectF(0, 0, *WINDOW_SIZE))
 
        #felt = QBrush(QPixmap(os.path.join('images','felt.png')))
        #self.scene.setBackgroundBrush(felt)

        #name = QGraphicsPixmapItem()
        #name.setPixmap(QPixmap(os.path.join('images','ronery.png')))
        #name.setPos(QPointF(170, 375))
        #self.scene.addItem(name)

        self.view.setScene(self.scene)
        gridLayout.addWidget(self.view, 0, 0)        
        
        # Create tree/dict structure out of list of blocks. Takes ~1 ms on Marc's machine
        block_tree = {}
        for block in six.itervalues(self.platform.blocks):
            if block.category: # blocks with None category should be left out for whatever reason (e.g. not installed)
                #print(block.category) # in list form, e.g. ['Core', 'Digital Television', 'ATSC']
                #print(block.label) # label GRC uses to name block
                #print(block.key) # actual block name (i.e. class name)
                #print('')

                # Add category if it's not in the tree yet
                if block.category[0] not in block_tree:
                    block_tree[block.category[0]] = {}

                if len(block.category) > 1:
                    if block.category[1] not in block_tree[block.category[0]]:
                        block_tree[block.category[0]][block.category[1]] = {}

                if len(block.category) > 2:
                    if block.category[2] not in block_tree[block.category[0]][block.category[1]]:
                        block_tree[block.category[0]][block.category[1]][block.category[2]] = {}

                # Add block to tree
                if len(block.category) == 1:
                    block_tree[block.category[0]][block.label] = {} # By using an empty dict instead of just a string, we keep the dict a pure tree of dicts and nothing else
                elif len(block.category) == 2:
                    block_tree[block.category[0]][block.category[1]][block.label] = {}
                elif len(block.category) == 3:
                    block_tree[block.category[0]][block.category[1]][block.category[2]][block.label] = {}
                else:
                    print("ERROR, SHOULD NOT HAVE THIS MANY CATEGORIES!")

        # Populate TreeView using recursive method. Takes ~1.5 ms on Marc's machine
        self._populateTree(block_tree, block_model.invisibleRootItem())

    # Recursive method of populating the tree
    def _populateTree(self, children, parent):
        for child in sorted(children):
            child_item = QStandardItem(child)
            child_item.setEditable(False)
            child_item.setDragEnabled(True)
            parent.appendRow(child_item)
            if bool(children): # if dict is not empty it will return True
                parent.setDragEnabled(False) # categories should not be draggable
                self._populateTree(children[child], child_item)
                


