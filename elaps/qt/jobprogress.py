#!/usr/bin/env python
"""Job progress tracker in ELAPS:PlayMat."""
from __future__ import division, print_function

import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot


class QJobProgress(QtGui.QDockWidget):

    """Tracker for job progresses in ELAPS:PlayMat."""

    def __init__(self, playmat):
        """Initialize the progress tracker."""
        QtGui.QDockWidget.__init__(
            self, "Job Progress",
            objectName="Job Progress",
            features=(QtGui.QDockWidget.DockWidgetMovable |
                      QtGui.QDockWidget.DockWidgetFloatable),
        )
        self.playmat = playmat

        self.timer = QtCore.QTimer(
            interval=1000,
            timeout=self.on_timer
        )

        self.UI_init()

    def UI_init(self):
        """Initialize the GUI elements."""
        self.playmat.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self)
        self.hide()

        self.setWidget(QtGui.QTreeWidget(
            selectionMode=QtGui.QListWidget.ExtendedSelection,
            contextMenuPolicy=QtCore.Qt.CustomContextMenu,
            itemDoubleClicked=self.on_double_click,
            customContextMenuRequested=self.on_rightclick
        ))
        self.widget().setHeaderLabels(
            ("job", "progress", "status")
        )

    def resize_columns(self):
        """Resize all columns."""
        for colid in range(3):
            self.widget().resizeColumnToContents(colid)

    def add_job(self, filebase, jobid, experiment):
        """Add a job to track."""
        job = {
            "jobid": jobid,
            "nresults": experiment.nresults(),
            "progress": 0,
            "filebase": filebase,
            "experiment": experiment.copy(),
            "stat": "PEND",
        }

        # item
        item = QtGui.QTreeWidgetItem(
            (os.path.basename(filebase), "", "pending")
        )
        self.widget().addTopLevelItem(item)

        job["item"] = item
        item.job = job

        # progress bar
        job["progressbar"] = QtGui.QProgressBar(
            maximum=job["nresults"]
        )
        self.widget().setItemWidget(item, 1, job["progressbar"])

        self.resize_columns()
        self.show()
        self.timer.start()

    # events
    @pyqtSlot()
    def on_timer(self):
        """Update progress."""
        # read data
        for itemid in range(self.widget().topLevelItemCount()):
            job = self.widget().topLevelItem(itemid).job
            if job["stat"] in ("ERROR", "DONE"):
                # job is done
                continue
            if not os.path.isfile(job["filebase"] + ".eer"):
                # job is pending
                continue
            with open(job["filebase"] + ".eer") as fin:
                job["progress"] = len(fin.readlines()) - 2
            if job["progress"] >= 0:
                job["stat"] = "RUN"
            if job["progress"] >= job["nresults"]:
                job["stat"] = "DONE"
            if os.path.isfile(job["filebase"] + ".err"):
                if os.path.getsize(job["filebase"] + ".err"):
                    job["stat"] = "FAIL"

        for itemid in range(self.widget().topLevelItemCount()):
            item = self.widget().topLevelItem(itemid)
            job = item.job
            progress = min(max(0, job["progress"]), job["nresults"])
            job["progressbar"].setValue(progress)
            if job["stat"] == "RUN":
                item.setText(
                    2, "%d / %d results" % (job["progress"], job["nresults"])
                )
            elif job["stat"] == "ERROR":
                item.setText(2, "error")
            elif job["stat"] == "DONE":
                item.setText(2, "done")

        self.resize_columns()

    @pyqtSlot(QtGui.QTreeWidgetItem, int)
    def on_double_click(self, item, col):
        """Event: double clicked on item."""
        if not item:
            return
        job = item.job
        if job["stat"] != "DONE":
            return
        self.playmat.on_open_viewer(job["filebase"] + ".eer")

    @pyqtSlot(QtCore.QPoint)
    def on_rightclick(self, pos):
        """Event: right click."""
        item = self.widget().itemAt(pos)
        if not item:
            return
        globalpos = self.widget().viewport().mapToGlobal(pos)
        job = item.job

        menu = QtGui.QMenu()

        # kill
        if job["stat"] in ("PEND", "RUN"):
            kill = QtGui.QAction(
                "Kill", menu, triggered=self.on_kill
            )
            kill.job = job
            menu.addAction(kill)

        # open
        elif job["stat"] == "DONE":
            open_ = QtGui.QAction(
                "Open in Viewer", menu, triggered=self.on_open
            )
            open_.job = job
            menu.addAction(open_)

        # remove
        remove = QtGui.QAction(
            "Remove", menu, triggered=self.on_remove
        )
        remove.job = job
        menu.addAction(remove)

        menu.exec_(globalpos)

    # @pyqtSlot()  # sender() pyqt bug
    def on_kill(self):
        """Event: kill job."""
        job = self.playmat.Qapp.sender().job
        job["experiment"]["backend"].kill(job["jobid"])
        self.on_remove()

    # @pyqtSlot()  # sender() pyqt bug
    def on_open(self):
        """Event: open job."""
        job = self.playmat.Qapp.sender().job
        self.playmat.on_open_viewer(job["filebase"] + ".eer")

    # @pyqtSlot()  # sender() pyqt bug
    def on_remove(self):
        """Event: remove job."""
        job = self.playmat.Qapp.sender().job
        self.widget().takeTopLevelItem(
            self.widget().indexOfTopLevelItem(job["item"])
        )
        if self.widget().topLevelItemCount() == 0:
            self.hide()
