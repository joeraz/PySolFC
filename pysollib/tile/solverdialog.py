#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

from pysollib.mfxutil import KwStruct
from pysollib.mygettext import _
from pysollib.tile.basetilemfxdialog import BaseTileMfxDialog
from pysollib.ui.tktile.solverdialog import BaseSolverDialog, solver_dialog

from .tkwidget import PysolCheckbutton, PysolCombo


# ************************************************************************
# *
# ************************************************************************

class SolverDialog(BaseSolverDialog, BaseTileMfxDialog):
    def _createGamesVar(self, frame, row):
        cb = PysolCombo(frame, values=tuple(self.gamenames),
                        selectcommand=self.gameSelected,
                        state='readonly', width=40,
                        fieldname=_("Game:"))
        cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        return cb

    def _createPresetVar(self, frame, row):
        cb = PysolCombo(frame, values=tuple(self.presets), state='readonly',
                        selectcommand=self._OnAssignToPreset,
                        fieldname=_("Preset:"))
        cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        cb.current(0)
        return cb

    def _createShowProgressButton(self, frame):
        return PysolCheckbutton(
            frame, variable=self.progress_var,
            text=_('Show progress'))

    def initKw(self, kw):
        strings = [_('&Start'), _('&Play'), _('&New'), 'sep', _('&Close'), ]
        kw = KwStruct(kw,
                      strings=strings,
                      default=0,
                      )
        return self._calc_MfxDialog().initKw(self, kw)

    def connectGame(self, game):
        name = self.app.getGameTitleName(game.id)
        if name in self.gamenames:
            self.start_button.config(state='normal')
            i = self.gamenames.index(name)
            self.games_var.current(i)
        else:
            self.start_button.config(state='disabled')
            self.games_var.current(0)
        self.play_button.config(state='disabled')


solver_dialog = solver_dialog


def create_solver_dialog(parent, game):
    global solver_dialog
    try:
        solver_dialog.top.wm_deiconify()
        solver_dialog.top.tkraise()
    except Exception:
        # traceback.print_exc()
        solver_dialog = SolverDialog(parent, game)


def raise_solver_dialog(game):
    try:
        if game.app.opt.topmost_dialogs:
            solver_dialog.top.tkraise()
            solver_dialog.top.attributes("-topmost", True)
        else:
            solver_dialog.top.attributes("-topmost", False)
    except Exception:
        pass


def unraise_solver_dialog():
    try:
        solver_dialog.top.attributes("-topmost", False)
    except Exception:
        pass
