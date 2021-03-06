An example task: checking for ext4 support
==========================================

Generating the skeleton using beaker-wizard
-------------------------------------------

The :ref:`beaker-wizard <beaker-wizard>` utility provides a guided step by
step method to create a task without the need to manually create all of the
necessary files. To get a basic idea of how we can use
:program:`beaker-wizard`, we will create a new task which will check the
platform supports the ext4 filesystem. If you have the ``beaker-client``
package installed, you should already have :program:`beaker-wizard`
available. You will also need to install the ``rhts-devel`` package.

The wizard supports creating various different kinds of tasks, but for this
example we're just going to use the default and create a task based on
`BeakerLib <https://fedorahosted.org/beakerlib>`__, a utility library
that makes it easier to write Beaker tasks as shell scripts.

Since Beaker was originally created to test distribution packages, new
tasks will typically be meant to test a particular package, and the
task directory will be named to match the package being tested. Many of
the questions in the wizard also assume that the task is being written
to test a particular package or bug fix.

For this example, however, we will simply create a directory with the
name ``mytask``. From your terminal, type::

     $ mkdir mytask
     $ cd mytask
     $ beaker-wizard

You will see a welcome message as follows::

    Welcome to The Beaker Wizard!
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    It seems, you're running the beaker-wizard for the first time.
    I'll try to be a little bit more verbose. Should you need
    any help in the future, just try using the "?" character.


    Bugs or CVE's related to the test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Supply one or more bug or CVE numbers (e.g. 123456 or 2009-7890). Use
    the '+' sign to add the bugs instead of replacing the current list.
    [None?] 

If you were writing this task to create a test related to a specific bug
recorded in `Red Hat Bugzilla <https://bugzilla.redhat.com>`__ you would
enter the bug ID or CVE reference number here.

Our example task, however, does not relate to a bug, so simply press the
return key. The wizard will then proceed to ask you several questions
regarding the test such as the description, the type of test, and
others. The wizard gives you choices for the answer wherever relevant,
but also has a default answer when one is not provided. Either enter
your own option or press return to accept the default answer::

    Test name
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Use few, well chosen words describing what the test does. Special
    chars will be automatically converted to dashes.
    [a-few-descriptive-words?] ext4-test

    What is the type of test?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Possible values: Regression, Performance, Stress, Certification,
    Security, Durations, Interoperability, Standardscompliance,
    Customeracceptance, Releasecriterium, Crasher, Tier1, Tier2, Alpha,
    KernelTier1, KernelTier2, Multihost, MultihostDriver, Install,
    FedoraTier1, FedoraTier2, KernelRTTier1, KernelReporting, Sanity
    Test type must be exactly one from the list above.
    [Sanity?] 

    Namespace
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Possible values: distribution, installation, kernel, desktop, tools,
    CoreOS, cluster, rhn, examples, performance, ISV, virt
    Provide a root namespace for the test.
    [CoreOS?] installation

    Short description
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Provide a short sentence describing the test.
    [What the test does?] Check whether ext4 filesystem is supported out of the box

    Time for test to run
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    The time must be in format [1-99][m|h|d] for 1-99 minutes/hours/days
    (e.g. 3m, 2h, 1d)
    [5m?] 

    Author's name
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Put your name [middle name] and surname here, abbreviations allowed.
    [Your Name?] Task Author

    Author's email
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Email address in lower case letters, dots and dashes. Underscore
    allowed before the "@" only.
    [user@hostname.com?] tauthor@example.com

    Ready to create the test, please review
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    /installation/mytask/Sanity/ext4-test

                 Namespace : installation
                   Package : mytask
                 Test type : Sanity
             Relative path : None
                 Test name : ext4-test
               Description : Check whether ext4 filesystem is supported out of the box

        Bug or CVE numbers : None
      Prefix the test name : Yes
      Reproducers to fetch : None

          Run for packages : mytask
         Required packages : mytask
             Architectures : All
                  Releases : All
                   Version : 1.0
                      Time : 5m

                  Priority : Normal
                   License : GPLv2+
              Confidential : No
               Destructive : No

                  Skeleton : beakerlib
                    Author : Task Author
                     Email : tauthor@example.com

    Type a few letters from field name to edit or press ENTER to confirm.
    Use the "write" keyword to save current settings as preferences.
    [Everything OK?] 

.. note::

   Some of the options in the wizard (notably the test type and namespace)
   currently have long lists of possible values that are actually only
   relevant to the initial Beaker instance created at Red Hat. They're only
   used to generate a suitable task name, so just pick whatever seems most
   appropriate for your task.

Once you have answered all the questions, the wizard allows you to
review the answers you have provided. As you can see, :program:`beaker-wizard`
assumed default values for some of the options such as ``Run for packages``,
``Required packages``, ``License`` and others without asking for more details.
As per the instructions displayed by the wizard, you can edit any of these or
the ones you specified earlier before creating the task. For example, if this
task is licensed under a license other than the default "GPLv2 or later", you
can change it, like so::

    [Everything OK?] Lic

    What licence should be used?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Just supply a license GPLv2+, GPLv3+, ...
    [GPLv2+?] GPLv3+

    Ready to create the test, please review
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ...

Once you have changed the value of License, you will again be able
to review all the options (and change if necessary). Finally, when you
are satisfied, press the enter key to create the task::

    Directory Sanity/ext4-test created
    File Sanity/ext4-test/PURPOSE written
    File Sanity/ext4-test/runtest.sh written
    File Sanity/ext4-test/Makefile written


Populating ``runtest.sh``
-------------------------

In the ``Sanity/ext4-test`` directory, you will notice that the three files:
``PURPOSE``, ``runtest.sh``, and a ``Makefile`` have been created. You
will see that ``PURPOSE`` will have the test description you entered
earlier along with the author's details. The ``runtest.sh`` file will
contain something similar to the following::

    #!/bin/bash
    # vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #   runtest.sh of /installation/mytask/Sanity/ext4-test
    #   Description: Check whether ext4 filesystem is supported out of the box
    #   Author: Task Author <tauthor@example.com>
    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #   Copyright (c) 2013 Red Hat, Inc.
    #
    #   This program is free software: you can redistribute it and/or
    #   modify it under the terms of the GNU General Public License as
    #   published by the Free Software Foundation, either version 2 of
    #   the License, or (at your option) any later version.
    #
    #   This program is distributed in the hope that it will be
    #   useful, but WITHOUT ANY WARRANTY; without even the implied
    #   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
    #   PURPOSE. See the GNU General Public License for more details.
    #
    #   You should have received a copy of the GNU General Public License
    #   along with this program. If not, see http://www.gnu.org/licenses/.
    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Include Beaker environment
    . /usr/bin/rhts-environment.sh || exit 1 
    . /usr/share/beakerlib/beakerlib.sh || exit 1 

    PACKAGE="mytask" 

    rlJournalStart
        rlPhaseStartSetup
            rlAssertRpm $PACKAGE
            rlRun "TmpDir=\$(mktemp -d)" 0 "Creating tmp directory"
            rlRun "pushd $TmpDir"
        rlPhaseEnd

        rlPhaseStartTest
            rlRun "touch foo" 0 "Creating the foo test file"
            rlAssertExists "foo"
            rlRun "ls -l foo" 0 "Listing the foo test file"
        rlPhaseEnd

        rlPhaseStartCleanup
            rlRun "popd"
            rlRun "rm -r $TmpDir" 0 "Removing tmp directory"
        rlPhaseEnd
    rlJournalPrintText
    rlJournalEnd

The "GPLv2 or later" license header in the beginning is the default for a
task. You can change the license to something more appropriate for your
needs during the task creation. :program:`beaker-wizard` will try to find
a license header corresponding to the specified license and if it is not
present will insert a default text where you can add the appropriate header
information and copyright notice. Please consult the :program:`beaker-wizard`
:ref:`man page <beaker-wizard>` for details on how you can add your own
license text using a preference file.

The package for which this task is defined is declared in the
``PACKAGE`` variable. We will simply delete this line since this task is
not for testing a package. Every BeakerLib-based task must begin with
``rlJournalStart``. This initializes the journaling functionality so
that the logging mechanism is initialized and your test results can
be saved. The functionality of a BeakerLib-based task is divided into
three stages: setup, start and cleanup, as indicated by the
``rlPhaseStartSetup``, ``rlPhaseStartTest`` and ``rlPhaseStartCleanup``
functions respectively.

The setup phase first checks if the package which we want to test is
available and then creates a temporary directory and moves there so that
all the test activities are performed in that directory.

The ``rlPhaseStartTest`` and its corresponding ``rlPhaseEnd``, encloses
the core test logic. Here, as you can see, the test is checking whether an
empty file has been created successfully or not. We will replace these
lines to include our own logic to check for the presence of ext4
support.

The cleanup phase is used to cleanup the working directory
created for the test and change back to the original working directory.
For our task, we don't need this.

The modified ``runtest.sh`` file looks like::

    #!/bin/bash
    # vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #   runtest.sh of /installation/mytask/Sanity/ext4-test
    #   Description: Check whether ext4 filesystem is supported out of the box
    #   Author: Task Author <tauthor@example.com>
    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #
    #   Copyright (c) 2013 Red Hat, Inc.
    #
    #   This copyrighted material is made available to anyone wishing
    #   to use, modify, copy, or redistribute it subject to the terms
    #   and conditions of the GNU General Public License version 2.
    #
    #   This program is distributed in the hope that it will be
    #   useful, but WITHOUT ANY WARRANTY; without even the implied
    #   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
    #   PURPOSE. See the GNU General Public License for more details.
    #
    #   You should have received a copy of the GNU General Public
    #   License along with this program; if not, write to the Free
    #   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
    #   Boston, MA 02110-1301, USA.
    #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Include Beaker environment
    . /usr/bin/rhts-environment.sh || exit 1
    . /usr/share/beakerlib/beakerlib.sh || exit 1

    rlJournalStart
        rlPhaseStartTest
            rlRun "cat /proc/filesystems | grep 'ext4'" 0 "Check if ext4 is supported"
        rlPhaseEnd
    rlJournalPrintText
    rlJournalEnd

You can now run this test locally to see if everything is correctly
working using ``make run``::

    # make run
    test -x runtest.sh || chmod a+x runtest.sh
    ./runtest.sh

    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    :: [   LOG    ] :: Test
    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

            ext4
    :: [   PASS   ] :: Check if ext4 is supported

    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    :: [   LOG    ] :: TEST PROTOCOL
    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    :: [   LOG    ] :: Test run ID   : oCNr6jM
    :: [   LOG    ] :: Package       : unknown
    :: [   LOG    ] :: Test started  : 2012-11-07 02:58:07 EST
    :: [   LOG    ] :: Test finished : 2012-11-07 02:58:07 EST
    :: [   LOG    ] :: Test name     : /installation/mytask/Sanity/ext4-test
    :: [   LOG    ] :: Distro:       : Red Hat Enterprise Linux Server release 6.3 (Santiago)
    :: [   LOG    ] :: Hostname      : hostname.example.com
    :: [   LOG    ] :: Architecture  : x86_64

    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    :: [   LOG    ] :: Test description
    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    PURPOSE of /installation/mytask/Sanity/ext4-test
    Description: Check whether ext4 filesystem is supported out of the box
    Author: Task Author <tauthor@example.com>


    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    :: [   LOG    ] :: Test
    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    :: [   PASS   ] :: Check if ext4 is supported
    :: [   LOG    ] :: Duration: 0s
    :: [   LOG    ] :: Assertions: 1 good, 0 bad
    :: [   PASS   ] :: RESULT: Test

    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    :: [   LOG    ] :: /installation/mytask/Sanity/ext4-test
    ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    :: [   LOG    ] :: Phases: 1 good, 0 bad
    :: [   PASS   ] :: RESULT: /installation/mytask/Sanity/ext4-test
    :: [02:58:07] ::  JOURNAL XML: /tmp/beakerlib-oCNr6jM/journal.xml
    :: [02:58:07] ::  JOURNAL TXT: /tmp/beakerlib-oCNr6jM/journal.txt

As you can see, the test passes with the logs saved in the above files.
Before we can upload this task to Beaker, we will have to package this
as an RPM. Both of these steps can be accomplished via ``make bkradd``
(assuming you have set your beaker client configuration successfully —
running ``bkr whoami`` is the easiest way to check that). If you do not
see any errors here, then you should see that this task has been uploaded to
the task library located at ``http://<your-beaker-instance>/tasks/``.

To learn more about the functions used to write the test, please see the
`BeakerLib documentation 
<https://fedorahosted.org/beakerlib/wiki/Manual>`__. You can learn
more about :program:`beaker-wizard` from its
:ref:`man page <beaker-wizard>`.

Running the task
----------------

Once the task is available in the "Task Library", you have to write a
job description (XML file) to run this test on a system provisioned in
Beaker (or else use one of the ``bkr`` client commands that will generate the
XML for you based on relevant command line parameters). Since our current
task is a simple one, we will look at the simple job description
needed to run this task explicitly::

    <job>
      <whiteboard>
        ext4 test
      </whiteboard>
      <recipeSet>
        <recipe>

          <distroRequires>
            <distro_arch op="=" value="x86_64" />
          </distroRequires>

          <hostRequires>
            <system_type value="Machine"/>
          </hostRequires>

          <task name="/installation/mytask/Sanity/ext4-test" role="STANDALONE"/>

        </recipe>
      </recipeSet>
    </job>

You can then submit the job (see :ref:`job-submission`). After the job has 
completed, you can access the logs as described in :ref:`job-results`.
You will see that on success, the ``TESTOUT.log``
file will contain the same log as when it was run locally. You can also obtain 
the logs using the :ref:`bkr job-logs <bkr-job-logs>` command. In some 
cases, in addition to the log files you may also want to retrieve some files 
from the test system. For example, in this case you may want to examine the 
contents of ``/proc/filesystems`` on the system that run the test. This can be 
done using the ``rhts-submit-log`` command or the ``rlFileSubmit`` function 
from BeakerLib.

The overall workflow of creating a task for a test, submitting a job to
run the test and accessing the test results is illustrated in 
:ref:`chronological-overview`.
