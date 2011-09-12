#
# Copyright (c) 2008 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#
#
# shell script function library for rhn-bootstrap
#
# $Id$

import string
import os.path


_header = """\
#!/bin/bash
echo "%s Client bootstrap script v4.0"

# This file was autogenerated. Minor manual editing of this script (and
# possibly the client-config-overrides.txt file) may be necessary to complete
# the bootstrap setup. Once customized, the bootstrap script can be triggered
# in one of two ways (the first is preferred):
#
#   (1) centrally, from the %s via ssh (i.e., from the
#       %s):
#         cd %s/bootstrap/
#         cat bootstrap-<edited_name>.sh | ssh root@<client-hostname> /bin/bash
#
#   ...or...
#
#   (2) in a decentralized manner, executed on each client, via wget or curl:
#         wget -qO- https://<hostname>/pub/bootstrap/bootstrap-<edited_name>.sh | /bin/bash
#         ...or...
#         curl -Sks https://<hostname>/pub/bootstrap/bootstrap-<edited_name>.sh | /bin/bash

# SECURITY NOTE:
#   Use of these scripts via the two methods discussed is the most expedient
#   way to register machines to your %s. Since "wget" is used
#   throughout the script to download various files, a "Man-in-the-middle"
#   attack is theoretically possible.
#
#   The actual registration process is performed securely via SSL, so the risk
#   is minimized in a sense. This message merely serves as a warning.
#   Administrators need to appropriately weigh their concern against the
#   relative security of their internal network.

# PROVISIONING/KICKSTART NOTE:
#   If provisioning a client, ensure the proper CA SSL public certificate is
#   configured properly in the post section of your kickstart profiles (the
#   %s or hosted web user interface).

# UP2DATE/RHN_REGISTER VERSIONING NOTE:
#   This script will not work with very old versions of up2date and
#   rhn_register.


echo
echo
echo "MINOR MANUAL EDITING OF THIS FILE MAY BE REQUIRED!"
echo
echo "If this bootstrap script was created during the initial installation"
echo "of a %s, the ACTIVATION_KEYS, and ORG_GPG_KEY values will"
echo "probably *not* be set (see below). If this is the case, please do the"
echo "following:"
echo "  - copy this file to a name specific to its use."
echo "    (e.g., to bootstrap-SOME_NAME.sh - like bootstrap-web-servers.sh.)"
echo "  - on the website create an activation key or keys for the system(s) to"
echo "    be registered."
echo "  - edit the values of the VARIABLES below (in this script) as"
echo "    appropriate:"
echo "    - ACTIVATION_KEYS needs to reflect the activation key(s) value(s)"
echo "      from the website. XKEY or XKEY,YKEY"
echo "    - ORG_GPG_KEY needs to be set to the name(s) of the corporate public"
echo "      GPG key filename(s) (residing in %s) if appropriate. XKEY or XKEY,YKEY"
echo
echo "Verify that the script variable settings are correct:"
echo "    - CLIENT_OVERRIDES should be only set differently if a customized"
echo "      client-config-overrides-VER.txt file was created with a different"
echo "      name."
echo "    - ensure the value of HOSTNAME is correct."
echo "    - ensure the value of ORG_CA_CERT is correct."
echo
echo "Enable this script: comment (with #'s) this block (or, at least just"
echo "the exit below)"
echo
%s

# can be edited, but probably correct (unless created during initial install):
# NOTE: ACTIVATION_KEYS *must* be used to bootstrap a client machine.
ACTIVATION_KEYS=%s
ORG_GPG_KEY=%s

# can be edited, but probably correct:
CLIENT_OVERRIDES=%s
HOSTNAME=%s

ORG_CA_CERT=%s
ORG_CA_CERT_IS_RPM_YN=%s

USING_SSL=%s
USING_GPG=%s

REGISTER_THIS_BOX=1

ALLOW_CONFIG_ACTIONS=%s
ALLOW_REMOTE_COMMANDS=%s

FULLY_UPDATE_THIS_BOX=%s

# Set if you want to specify profilename for client systems.
# NOTE: Make sure it's set correctly if any external command is used.
#
# ex. PROFILENAME="foo.example.com"  # For specific clinet system
#     PROFILENAME=`hostname -s`      # Short hostname
#     PROFILENAME=`hostname -f`      # FQDN
PROFILENAME=""   # Empty by default to let it be set automatically.

# After registration, before updating the system (or at least the installer)
# disable all repos not provided by SUSE Manager.
DISABLE_LOCAL_REPOS=1

# SUSE Manager Specific settings:
#
# - Alternate location of the client tool repos providing the zypp-plugin-spacewalk
# and packges required for registration. Unless they are already installed on the
# client this repo is expected to provide them for SLE-10/SLE-11 based clients:
#   ${Z_CLIENT_REPOS_ROOT}/sle/VERSION/PATCHLEVEL
# If empty, the SUSE Manager repositories provided at https://${HOSTNAME}/pub/repositories
# are used.
Z_CLIENT_REPOS_ROOT=

#
# -----------------------------------------------------------------------------
# DO NOT EDIT BEYOND THIS POINT -----------------------------------------------
# -----------------------------------------------------------------------------
#

# an idea from Erich Morisse (of Red Hat).
# use either wget *or* curl
# Also check to see if the version on the
# machine supports the insecure mode and format
# command accordingly.

if [ -x /usr/bin/wget ] ; then
    output=`LANG=en_US /usr/bin/wget --no-check-certificate 2>&1`
    error=`echo $output | grep "unrecognized option"`
    if [ -z "$error" ] ; then
        FETCH="/usr/bin/wget -q -r -nd --no-check-certificate"
    else
        FETCH="/usr/bin/wget -q -r -nd"
    fi

else
    if [ -x /usr/bin/curl ] ; then
        output=`LANG=en_US /usr/bin/curl -k 2>&1`
        error=`echo $output | grep "is unknown"`
        if [ -z "$error" ] ; then
            FETCH="/usr/bin/curl -SksO"
        else
            FETCH="/usr/bin/curl -SsO"
        fi
    fi
fi
HTTP_PUB_DIRECTORY=http://${HOSTNAME}/%s
HTTPS_PUB_DIRECTORY=https://${HOSTNAME}/%s
if [ $USING_SSL -eq 0 ] ; then
    HTTPS_PUB_DIRECTORY=${HTTP_PUB_DIRECTORY}
fi

INSTALLER=up2date
if [ -x /usr/bin/zypper ] ; then
    INSTALLER=zypper
elif [ -x /usr/bin/yum ] ; then
    INSTALLER=yum
fi

if [ ! -w . ] ; then
    echo ""
    echo "*** ERROR: $(pwd):"
    echo "    No permission to write to the current directory."
    echo "    Please execute this script in a directory where downloaded files can be stored."
    echo ""
    exit 1
fi
"""


def getHeader(productName, activation_keys, org_gpg_key,
              overrides, hostname, orgCACert, isRpmYN,
              using_ssl, using_gpg,
              allow_config_actions, allow_remote_commands, up2dateYN, pubname, apachePubDirectory):
    #2/14/06 wregglej 181407 If the org_gpg_key option has the path to the file
    #in it, remove it. It will cause the $FETCH to fail.
    path_list = os.path.split(org_gpg_key)
    if path_list[0] and path_list[0] != '':
        org_gpg_key = path_list[1]

    if not activation_keys:
        exit_call = "exit 1"
    else:
        exit_call = " "

    return _header % (productName, productName, productName, apachePubDirectory, productName, productName, productName, apachePubDirectory,
                      exit_call, activation_keys, org_gpg_key,
                      overrides, hostname, orgCACert, isRpmYN,
                      using_ssl, using_gpg,
                      allow_config_actions, allow_remote_commands, up2dateYN,
                      pubname, pubname)


def getRegistrationStackSh():
    return """\
if [ "$INSTALLER" == zypper ]; then
  echo
  echo "CHECKING THE REGISTRATION STACK"
  echo "-------------------------------------------------"

  function getZ_CLIENT_CODE_BASE() {
    local BASE=""
    local VERSION=""
    local PATCHLEVEL=""
    test -r /etc/SuSE-release && {
      grep -q 'Enterprise' /etc/SuSE-release && BASE="sle"
      eval $(grep '^\(VERSION\|PATCHLEVEL\)' /etc/SuSE-release | tr -d '[:blank:]')
    }
    Z_CLIENT_CODE_BASE="${BASE:-unknown}"
    Z_CLIENT_CODE_VERSION="${VERSION:-unknown}"
    Z_CLIENT_CODE_PATCHLEVEL="${PATCHLEVEL:-0}"
  }

  function getZ_MISSING() {
    local NEEDED="spacewalk-check spacewalk-client-setup spacewalk-client-tools zypp-plugin-spacewalk"
    Z_MISSING=""
    for P in $NEEDED; do
      rpm -q "$P" || Z_MISSING="$Z_MISSING $P"
    done
  }

  function getZ_ZMD_TODEL() {
    local ZMD_STACK="zmd rug libzypp-zmd-backend yast2-registration zen-updater zmd-inventory suseRegister-jeos"
    if rpm -q suseRegister --qf '%{VERSION}' | grep -q '^\(0\.\|1\.[0-3]\)\(\..*\)\?$'; then
      # we need the new suseRegister >= 1.4, so wipe an old one too
      ZMD_STACK="$ZMD_STACK suseRegister suseRegisterInfo spacewalk-client-tools"
    fi
    Z_ZMD_TODEL=""
    for P in $ZMD_STACK; do
      rpm -q "$P" && Z_ZMD_TODEL="$Z_ZMD_TODEL $P"
    done
  }

  echo "* check for necessary packages being installed..."
  # client codebase determines repo url to use and whether additional
  # preparations are needed before installing the missing packages.
  getZ_CLIENT_CODE_BASE
  echo "* client codebase is ${Z_CLIENT_CODE_BASE}-${Z_CLIENT_CODE_VERSION}-sp${Z_CLIENT_CODE_PATCHLEVEL}"

  getZ_MISSING
  if [ -z "$Z_MISSING" ]; then
    echo "  no packages missing."
  else
    echo "* going to install missing packages..."
    Z_CLIENT_REPOS_ROOT="${Z_CLIENT_REPOS_ROOT:-http://${HOSTNAME}/pub/repositories}"
    Z_CLIENT_REPO_URL="${Z_CLIENT_REPOS_ROOT}/${Z_CLIENT_CODE_BASE}/${Z_CLIENT_CODE_VERSION}/${Z_CLIENT_CODE_PATCHLEVEL}/bootstrap"
    test "${Z_CLIENT_CODE_BASE}/${Z_CLIENT_CODE_VERSION}/${Z_CLIENT_CODE_PATCHLEVEL}" = "sle/11/1" && {
      # use backward compatible URL for SLE11-SP1 repo
      Z_CLIENT_REPO_URL="${Z_CLIENT_REPOS_ROOT}/susemanager-client-setup"
    }
    Z_CLIENT_REPO_NAME="susemanager-client-setup"
    Z_CLIENT_REPO_FILE="/etc/zypp/repos.d/$Z_CLIENT_REPO_NAME.repo"

    # code10 requires removal of the ZMD stack first
    if [ "$Z_CLIENT_CODE_BASE" == "sle" ]; then
      if [ "$Z_CLIENT_CODE_VERSION" = "10" ]; then
	echo "* check whether to remove the ZMD stack first..."
	getZ_ZMD_TODEL
	if [ -z "$Z_ZMD_TODEL" ]; then
	  echo "  ZMD stack is not installed. No need to remove it."
	else
	  echo "  Disable and remove the ZMD stack..."
	  # stop any running zmd
	  if [ -x /usr/sbin/rczmd ]; then
	    /usr/sbin/rczmd stop
	  fi
	  rpm -e $Z_ZMD_TODEL || {
	    echo "ERROR: Failed remove the ZMD stack."
	    exit 1
	  }
	fi
      fi
    fi

    # way to add the client software repository depends on the zypp version actually
    # installed (original code 10 via 'zypper sa', or code 11 like via .repo files)
    #
    # Note: We try to install the missing packages even if adding the repo fails.
    # Might be some other system repo provides them instead.
    echo "  adding client software repository at $Z_CLIENT_REPO_URL"
    if rpm -q zypper --qf '%{VERSION}' | grep -q '^0\(\..*\)\?$'; then

      # code10 zypper has no --gpg-auto-import-keys and no reliable return codes.
      zypper --non-interactive --no-gpg-checks sd $Z_CLIENT_REPO_NAME
      zypper --non-interactive --no-gpg-checks sa $Z_CLIENT_REPO_URL $Z_CLIENT_REPO_NAME
      zypper --non-interactive --no-gpg-checks refresh "$Z_CLIENT_REPO_NAME"
      zypper --non-interactive --no-gpg-checks in $Z_MISSING
      for P in $Z_MISSING; do
	rpm -q "$P" || {
	  echo "ERROR: Failed to install all missing packages."
	  exit 1
	}
      done
      # Now as code11 zypper is installed, create the .repo file
      cat <<EOF >"$Z_CLIENT_REPO_FILE"
[$Z_CLIENT_REPO_NAME]
name=$Z_CLIENT_REPO_NAME
baseurl=$Z_CLIENT_REPO_URL
enabled=1
autorefresh=1
keeppackages=0
gpgcheck=0
EOF
    else

      # On code11 simply add the repo and then install
      cat <<EOF >"$Z_CLIENT_REPO_FILE"
[$Z_CLIENT_REPO_NAME]
name=$Z_CLIENT_REPO_NAME
baseurl=$Z_CLIENT_REPO_URL
enabled=1
autorefresh=1
keeppackages=0
gpgcheck=0
EOF
      zypper --non-interactive --gpg-auto-import-keys refresh "$Z_CLIENT_REPO_NAME"
      zypper --non-interactive in $Z_MISSING || {
	  echo "ERROR: Failed to install all missing packages."
	  exit 1
	}

    fi
  fi

  # on code10 we need to convert metadata of installed products
  if [ "$Z_CLIENT_CODE_BASE" == "sle" ]; then
    if [ "$Z_CLIENT_CODE_VERSION" = "10" ]; then
      test -e "/usr/share/zypp/migrate/10-11.migrate.products.sh" && {
	echo "* check whether we have to to migrate metadata..."
	sh /usr/share/zypp/migrate/10-11.migrate.products.sh || {
	  echo "ERROR: Failed to migrate product metadata."
	  exit 1
	}
      }
    fi
  fi
fi

"""


def getConfigFilesSh():
    return """\
echo
echo "UPDATING RHN_REGISTER/UP2DATE CONFIGURATION FILES"
echo "-------------------------------------------------"
echo "* downloading necessary files"
echo "  client_config_update.py..."
rm -f client_config_update.py
$FETCH ${HTTPS_PUB_DIRECTORY}/bootstrap/client_config_update.py
echo "  ${CLIENT_OVERRIDES}..."
rm -f ${CLIENT_OVERRIDES}
$FETCH ${HTTPS_PUB_DIRECTORY}/bootstrap/${CLIENT_OVERRIDES}

if [ ! -f "client_config_update.py" ] ; then
    echo "ERROR: client_config_update.py was not downloaded"
    exit 1
fi
if [ ! -f "${CLIENT_OVERRIDES}" ] ; then
    echo "ERROR: ${CLIENT_OVERRIDES} was not downloaded"
    exit 1
fi

"""


def getUp2dateScriptsSh():
    return """\
echo "* running the update scripts"
if [ -f "/etc/sysconfig/rhn/rhn_register" ] ; then
    echo "  . rhn_register config file"
    /usr/bin/python -u client_config_update.py /etc/sysconfig/rhn/rhn_register ${CLIENT_OVERRIDES}
fi
if [ -f "/etc/sysconfig/rhn/up2date" ] ; then
  echo "  . up2date config file"
  /usr/bin/python -u client_config_update.py /etc/sysconfig/rhn/up2date ${CLIENT_OVERRIDES}
fi

"""


def getGPGKeyImportSh():
    return """\
echo
echo "PREPARE GPG KEYS AND CORPORATE PUBLIC CA CERT"
echo "-------------------------------------------------"
if [ ! -z "$ORG_GPG_KEY" ] ; then
    echo
    echo "* importing organizational GPG keys"
    for GPG_KEY in $(echo "$ORG_GPG_KEY" | tr "," " "); do
	rm -f ${GPG_KEY}
	$FETCH ${HTTPS_PUB_DIRECTORY}/${GPG_KEY}
	# get the major version of up2date
	# this will also work for RHEL 5 and systems where no up2date is installed
	res=$(LC_ALL=C rpm -q --queryformat '%{version}' up2date | sed -e 's/\..*//g')
	if [ "x$res" == "x2" ] ; then
	    gpg $(up2date --gpg-flags) --import $GPG_KEY
	else
	    rpm --import $GPG_KEY
	fi
    done
else
    echo "* no organizational GPG keys to import"
fi

"""


def getCorpCACertSh():
    return """\
echo
if [ $USING_SSL -eq 1 ] ; then
    echo "* attempting to install corporate public CA cert"
    test -d /usr/share/rhn || mkdir -p /usr/share/rhn
    if [ $ORG_CA_CERT_IS_RPM_YN -eq 1 ] ; then
        rpm -Uvh --force --replacefiles --replacepkgs ${HTTP_PUB_DIRECTORY}/${ORG_CA_CERT}
    else
        rm -f ${ORG_CA_CERT}
        $FETCH ${HTTP_PUB_DIRECTORY}/${ORG_CA_CERT}
        mv ${ORG_CA_CERT} /usr/share/rhn/
    fi
    if [ "$INSTALLER" == zypper ] ; then
	if [  $ORG_CA_CERT_IS_RPM_YN -eq 1 ] ; then
	  # get name from config
	  ORG_CA_CERT=$(basename $(sed -n 's/^sslCACert *= *//p' "${CLIENT_OVERRIDES}"))
	fi
	test -e "/etc/ssl/certs/${ORG_CA_CERT}.pem" || {
	  test -d "/etc/ssl/certs" || mkdir -p "/etc/ssl/certs"
	  ln -s "/usr/share/rhn/${ORG_CA_CERT}" "/etc/ssl/certs/${ORG_CA_CERT}.pem"
	}
	test -x /usr/bin/c_rehash && /usr/bin/c_rehash /etc/ssl/certs/ | grep "${ORG_CA_CERT}"
    fi
else
    echo "* configured not to use SSL: don't install corporate public CA cert"
fi

"""


#5/16/05 wregglej 159437 - changed script to use rhn-actions-control
def getAllowConfigManagement():
    return """\
if [ $ALLOW_CONFIG_ACTIONS -eq 1 ] ; then
    echo
    echo "* setting permissions to allow configuration management"
    echo "  NOTE: use an activation key to subscribe to the tools"
    if [ "$INSTALLER" == zypper ] ; then
        echo "        channel and zypper install/update rhncfg-actions"
    elif [ "$INSTALLER" == yum ] ; then
        echo "        channel and yum upgrade rhncfg-actions"
    else
        echo "        channel and up2date rhncfg-actions"
    fi
    if [ -x "/usr/bin/rhn-actions-control" ] ; then
        rhn-actions-control --enable-all
        rhn-actions-control --disable-run
    else
        echo "Error setting permissions for configuration management."
        echo "    Please ensure that the activation key subscribes the"
	if [ "$INSTALLER" == zypper ] ; then
	    echo "    system to the tools channel and zypper install/update rhncfg-actions."
	elif [ "$INSTALLER" == yum ] ; then
            echo "    system to the tools channel and yum updates rhncfg-actions."
        else
            echo "    system to the tools channel and up2dates rhncfg-actions."
        fi
        exit
    fi
fi

"""


#5/16/05 wregglej 158437 - changed script to use rhn-actions-control
def getAllowRemoteCommands():
    return """\
if [ $ALLOW_REMOTE_COMMANDS -eq 1 ] ; then
    echo
    echo "* setting permissions to allow remote commands"
    echo "  NOTE: use an activation key to subscribe to the tools"
    if [ "$INSTALLER" == zypper ] ; then
        echo "        channel and zypper update rhncfg-actions"
    elif [ "$INSTALLER" == yum ] ; then
        echo "        channel and yum upgrade rhncfg-actions"
    else
        echo "        channel and up2date rhncfg-actions"
    fi
    if [ -x "/usr/bin/rhn-actions-control" ] ; then
        rhn-actions-control --enable-run
    else
        echo "Error setting permissions for remote commands."
        echo "    Please ensure that the activation key subscribes the"
        if [ "$INSTALLER" == zypper ] ; then
	    echo "    system to the tools channel and zypper updates rhncfg-actions."
	elif [ "$INSTALLER" == yum ] ; then
            echo "    system to the tools channel and yum updates rhncfg-actions."
        else
            echo "    system to the tools channel and up2dates rhncfg-actions."
        fi
        exit
    fi
fi

"""


def getRegistrationSh(productName):
    return """\
echo
echo "REGISTRATION"
echo "------------"
# Should have created an activation key or keys on the %s's
# website and edited the value of ACTIVATION_KEYS above.
#
# If you require use of several different activation keys, copy this file and
# change the string as needed.
#
if [ -z "$ACTIVATION_KEYS" ] ; then
    echo "*** ERROR: in order to bootstrap %s clients, an activation key or keys"
    echo "           must be created in the %s web user interface, and the"
    echo "           corresponding key or keys string (XKEY,YKEY,...) must be mapped to"
    echo "           the ACTIVATION_KEYS variable of this script."
    exit 1
fi

if [ $REGISTER_THIS_BOX -eq 1 ] ; then
    echo "* registering"
    files=""
    directories=""
    if [ $ALLOW_CONFIG_ACTIONS -eq 1 ] ; then
        for i in "/etc/sysconfig/rhn/allowed-actions /etc/sysconfig/rhn/allowed-actions/configfiles"; do
            [ -d "$i" ] || (mkdir -p $i && directories="$i $directories")
        done
        [ -f /etc/sysconfig/rhn/allowed-actions/configfiles/all ] || files="$files /etc/sysconfig/rhn/allowed-actions/configfiles/all"
        [ -n "$files" ] && touch  $files
    fi
    if [ -z "$PROFILENAME" ] ; then
        profilename_opt=""
    else
        profilename_opt="--profilename=$PROFILENAME"
    fi
    /usr/sbin/rhnreg_ks --force --activationkey "$ACTIVATION_KEYS" $profilename_opt
    RET="$?"
    [ -n "$files" ] && rm -f $files
    [ -n "$directories" ] && rmdir $directories
    if [ $RET -eq 0 ]; then
      echo
      echo "*** this system should now be registered, please verify ***"
      echo
    else
      echo
      echo "*** Error: Registering the system failed."
      echo
      exit 1
    fi
else
    echo "* explicitely not registering"
fi

""" % (productName, productName, productName)


def getUp2dateTheBoxSh(productName):
    return """\
echo
echo "OTHER ACTIONS"
echo "------------------------------------------------------"
if [ $DISABLE_LOCAL_REPOS -eq 1 ]; then
    if [ "$INSTALLER" == zypper ] ; then
	echo "* Disable all repos not provided by SUSE Manager Server."
	zypper ms -d --all
	zypper ms -e --medium-type plugin
	zypper mr -d --all
	zypper mr -e --medium-type plugin
	zypper mr -e "$Z_CLIENT_REPO_NAME"
    elif [ "$INSTALLER" == yum ] ; then
        echo "* Disable all repos not provided by SUSE Manager Server.";
	for F in /etc/yum.repos.d/*.repo; do
	  test -f "$F" || continue
	  sed -i 's/^enabled=1/enabled=0/' "$F"
	done
    fi
fi
if [ $FULLY_UPDATE_THIS_BOX -eq 1 ] ; then
    if [ "$INSTALLER" == zypper ] ; then
        echo "zypper --non-interactive up zypper zypp-plugin-spacewalk; rhn-profile-sync; zypper --non-interactive up (conditional)"
    elif [ "$INSTALLER" == yum ] ; then
        echo "yum -y upgrade yum yum-rhn-plugin; rhn-profile-sync; yum upgrade (conditional)"
    else
        echo "up2date up2date; up2date -p; up2date -uf (conditional)"
    fi
else
    if [ "$INSTALLER" == zypper ] ; then
        echo "zypper --non-interactive up zypper zypp-plugin-spacewalk; rhn-profile-sync"
    elif [ "$INSTALLER" == yum ] ; then
        echo "yum -y upgrade yum yum-rhn-plugin; rhn-profile-sync"
    else
        echo "up2date up2date; up2date -p"
    fi
fi
echo "but any post configuration action can be added here.  "
echo "------------------------------------------------------"
if [ $FULLY_UPDATE_THIS_BOX -eq 1 ] ; then
    echo "* completely updating the box"
else
    echo "* ensuring $INSTALLER itself is updated"
fi
if [ "$INSTALLER" == zypper ] ; then
    zypper lr -u
    zypper --non-interactive ref -s
    zypper --non-interactive up zypper zypp-plugin-spacewalk
    if [ -x /usr/sbin/rhn-profile-sync ] ; then
        /usr/sbin/rhn-profile-sync
    else
        echo "Error updating system info in %s."
        echo "    Please ensure that rhn-profile-sync in installed and rerun it."
    fi
    if [ $FULLY_UPDATE_THIS_BOX -eq 1 ] ; then
        zypper --non-interactive up
    fi
elif [ "$INSTALLER" == yum ] ; then
    yum repolist
    /usr/bin/yum -y upgrade yum yum-rhn-plugin
    if [ -x /usr/sbin/rhn-profile-sync ] ; then
        /usr/sbin/rhn-profile-sync
    else
        echo "Error updating system info in %s."
        echo "    Please ensure that rhn-profile-sync in installed and rerun it."
    fi
    if [ $FULLY_UPDATE_THIS_BOX -eq 1 ] ; then
        /usr/bin/yum -y upgrade
    fi
else
    /usr/sbin/up2date up2date
    /usr/sbin/up2date -p
    if [ $FULLY_UPDATE_THIS_BOX -eq 1 ] ; then
        /usr/sbin/up2date -uf
    fi
fi
echo "-bootstrap complete-"
""" % (productName, productName)









