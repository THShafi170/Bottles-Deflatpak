# portal.py
#
# Copyright 2025 mirkobrombin <brombin94@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, in version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gi


class PortalUtils:
    """
    Utility class for interacting with XDG Desktop Portals safely.
    """

    @staticmethod
    def get_portal():
        """
        Safely attempt to get an Xdp.Portal instance.
        Returns:
            Xdp.Portal or None if not available.
        """
        try:
            gi.require_version("Xdp", "1.0")
            from gi.repository import Xdp  # type: ignore

            return Xdp.Portal()
        except (ImportError, ValueError):
            return None

    @staticmethod
    def is_available() -> bool:
        """
        Check if the XDP namespace and portal service are available.
        """
        portal = PortalUtils.get_portal()
        return portal is not None
