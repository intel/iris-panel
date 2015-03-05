=====================
 IRIS Testing Process
=====================

This document describe the steps of how to setup iris service locally and having tests.

Note: Every release has a version number, let’s assume this release is 0.2.2 for reference.

Preparation: get ansible related project
----------------------------------------

- clone iris playbook:

 $ git clone ssh://user@otctools.jf.intel.com:29418/infrastructure/ansible/playbooks/iris
 $ cd iris
 $ git checkout –b release-for-0.2.2 0.2.2
 
 There is a VagrantFile inside above git repo. We will use vagrant to launch a vm for testing.

- clone common roles project:

 $ git clone ssh://user@otctools.jf.intel.com:29418/infrastructure/ansible/roles
 $ cd roles
 $ git checkout –b release-for-0.2.2 0.2.2

 **Note**
 Please add above roles path to ansible roles_path config. For exmaple change your ~/.ansible.cfg like this:
 [defaults]
 roles_path = /home/xxx/roles

Upgrading Testing
------------------

- install last old version iris, here it is 0.2.1

 * change to your iris playbook directory

 * make sure the repo in file “host_vars/vagrant” refers to 0.2.1 in tizen org:

 http://download.tizen.org/iris/latest-release/openSUSE_13.1/

 * run playbook to deploy
 
 $ vagrant provision

 * Check the iris version inside vagrant vm is 0.2.1

- import online data to old iris

 * dump productional data
 
 $ mysqldump -hhostname -uusername -ppassword dbname > 021.sql

 * inside vagrant vm import this data

 $ cat 021.sql | mysql -uroot testdb

- upgrade iris to new version

 * change repo in “host_vars/vagrant” to testing repo

 like http://download.otctools.jf.intel.com/staging/iris/archive/0.2.2/openSUSE_13.1/

 * run playbook again
 
 $ vagrant provision

 * check iris version again, it should be 0.2.2 now
