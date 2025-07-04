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

import math

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.mygettext import _
from pysollib.stack import \
        AbstractFoundationStack, \
        OpenStack, \
        SS_FoundationStack, \
        SS_RowStack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ANY_RANK, ANY_SUIT, NO_RANK, UNLIMITED_ACCEPTS, \
        UNLIMITED_CARDS,  UNLIMITED_MOVES


# ************************************************************************
#  * Master Deck Stacks
#  ***********************************************************************/


class Master_FoundationStack(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_move=0)
        SS_FoundationStack.__init__(self, x, y, game, suit, **cap)

    def updateText(self):
        AbstractFoundationStack.updateText(self)
        self.game.updateText()


class Triumph_Foundation(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=12, dir=0, base_rank=NO_RANK, max_move=0)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):

        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return 1
        stack_dir = self.game.getFoundationDir()
        if stack_dir == 0:
            card_dir = (cards[0].rank - self.cards[-1].rank) % self.cap.mod
            return card_dir in (1, 11)
        return (self.cards[-1].rank + stack_dir) % self.cap.mod \
            == cards[0].rank


# ************************************************************************
#  * Master Row Stacks
#  ***********************************************************************/

class Master_OpenStack(OpenStack):

    def __init__(self, x, y, game, yoffset, **cap):
        kwdefault(cap, max_move=UNLIMITED_MOVES, max_cards=UNLIMITED_CARDS,
                  max_accept=UNLIMITED_ACCEPTS, base_rank=0, dir=-1)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def isRankSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not c1.rank + dir == c2.rank:
                return 0
            c1 = c2
        return 1

    def isAlternateColorSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not ((c1.suit + c2.suit) % 2 and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isSuitSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not (c1.suit == c2.suit and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1


class Master_RK_RowStack(Master_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards) or
                not self.isRankSequence(cards)):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isRankSequence([stackcards[-1], cards[0]])


class Master_SS_RowStack(Master_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards) or
                not self.isSuitSequence(cards)):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isSuitSequence([stackcards[-1], cards[0]])

# ************************************************************************
#  *
#  ***********************************************************************/

class AbstractMasterGame(Game):

    SUITS = (_("Diamond"), _("Heart"), _("Club"), _("Spade"),
             _("Crown"), _("Star"), _("Lightning"), _("Anchor"),
             _("Circle"), _("Moon"), _("Triangle"), _("Book"),
             _("Cross"), _("Nut"), _("Pentagon"), _("Explosion"))
    RANKS = (_("Ace"), "2", "3", "4", "5", "6", "7", "8", "9", "10",
             "11", "12", _("Jack"), _("Knight"), _("Queen"), _("King"))

    def updateText(self):
        pass

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank)

    def parseCard(self, card):
        if not card.face_up:
            return _("Face-down")
        suit = self.SUITS[card.suit]
        rank = self.RANKS[card.rank]
        return rank + " - " + suit

# ************************************************************************
#  * Unobtanium
#  ***********************************************************************/

class Unobtanium(AbstractMasterGame):
    Layout_Method = staticmethod(Layout.klondikeLayout)
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SS_RowStack
    BASE_RANK = ANY_RANK
    MAX_MOVE = 0

    #
    # Game layout
    #

    def createGame(self, max_rounds=-1, num_deal=2, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=16, waste=1)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(
            l.s.talon.x, l.s.talon.y, self,
            max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(
                self.Foundation_Class(
                    r.x, r.y, self,
                    r.suit, mod=16, max_cards=16, max_move=self.MAX_MOVE))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(
                self.RowStack_Class(
                    r.x, r.y, self,
                    suit=ANY_SUIT, base_rank=self.BASE_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        for i in range(16):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


# ************************************************************************
# *
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level,
      altnames=()):
    game_type = game_type | GI.GT_MASTER_DECK
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  suits=list(range(16)), ranks=list(range(16)),
                  altnames=altnames)
    registerGame(gi)
    return gi

r(17000, Unobtanium, 'Unobtanium', GI.GT_MASTER_DECK, 1, -1,
  GI.SL_BALANCED)

del r
