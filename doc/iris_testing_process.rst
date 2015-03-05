=====================
 IRIS Testing Process
=====================
We use ansible to deploy iris to vagrant for testing, so here we split our testing into four main parts:

1. Preparation: get ansible related project

2. Init vagrant

    2.1 configured vagrant

    2.2 first time to vagrant world

3. Upgrading Testing

    3.1 install last old version iris

    3.2 import online data to old iris

    3.3 upgrade iris to new version

4. Feature and bug Testing

    4.1 testing based on fixed bugs and new features

The following is the details:

Note: every release has a version number, let’s assume this release is 0.2.2 for reference.

Preparation: get ansible related project
----------------------------------------
.. _iris ansible playbook:

1. clone iris playbook:

   $git clone ssh://user@otctools.jf.intel.com:29418/infrastructure/ansible/playbooks/iris (make sure you can access gerrit)

   $cd iris

   $git checkout –b release-for-0.2.2 0.2.2

   **Note**:

        1. 0.2.2 is tag name for this release, it would change due to release, you can run "$git tag -l" to check.

        2. release-for-0.2.2 is branch name, you can name it to whatever meets git naming convention

2. clone common roles project:

   $git clone ssh://user@otctools.jf.intel.com:29418/infrastructure/ansible/roles (make sure you can access gerrit)

   $cd roles

   $git checkout –b release-for-0.2.2 0.2.2

   **Note**:

        1. 0.2.2 is tag name for this release, it would change due to release, you can run "$git tag -l" to check

        2. release-for-0.2.2 is branch name, you can name it to whatever meets git naming convention

        3. here we should make ansible knows the common role path (suppose you locate it in: /home/xxx/roles), add the

           following line to ~/.ansible.cfg (if this file doesn’t exist, create it by yourself):

           [defaults]

           roles_path = /home/xxx/roles

Init vagrant
------------
1. configured vagrant:

   1.1 change to your vagrant directory

   1.2 $vagrant destroy

   1.3 $vagrant up

2. first time to vagrant world:

   **DOC**: https://www.vagrantup.com/

   2.1 install vagrant and provider (here we use virtualbox)

       2.1.1 with software manager, suppose your system is ubuntu:

             $sudo apt-get install vagrant virtualbox

       2.1.2 or download the package:

            `vagrant <https://www.vagrantup.com/downloads.html>`_

            `virtualbox <https://www.virtualbox.org/wiki/Downloads>`_

            $sudo dpkg -i xxx.deb or $sudo rpm -i xxx.rpm

  2.2 configure vagrant

      2.2.1 $mkdir vagarant

      2.2.2 $vagrant init (then you can see "Vagrantfile" is created)

      2.2.3 add the following content to "Vagrantfile":

            config.vm.box = "openSUSE_131_64"

            config.vm.box_url = "http://go.bj.intel.com/vagrant/boxes/opensuse/openSUSE_13.1_64.box"

            config.ssh.private_key_path = "/home/xxxx/.ssh/key_for_vagrant_ssh.id_rsa"

            config.vm.network :forwarded_port, guest: 8000, host: 8082

           **Note**:
                1. maybe config.vm.box has been in the file, you can just modify the name

                2. for iris, we just test it on opensuse13.1 64bit, so here we use openSUSE_13.1_64.box

                3. private_key: please download it from:

                   http://go.bj.intel.com/vagrant/configs/key_for_vagrant_ssh.id_rsa

                   and put it in your directory: ~/.ssh/, remember to change 'xxx' to your username.

                4. network port: here I use 8082, you can use any one like 8081, 8083, better if larger than 8000

                5. about ssh port, if only one vagrant active on your host, the default is 2222, you can check it

                   by "$vagrant ssh-config", if not 2222, remember to update "ansible_ssh_port" in file "vagrant" in

                   `iris ansible playbook`_ cloned before like bellow:

                   [vagrant]
                   vagrant ansible_ssh_port=2222 ansible_ssh_host=localhost...

      2.2.4 connect to vagrant

            $vagrant up

            $vagrant ssh (then you can enter the vagrant vm)

Upgrading Testing
------------------
1. install last old version iris, here it is 0.2.1

    1.1 change to your iris playbook directory

    1.2 make sure the repo in file “host_vars/vagrant” refers to 0.2.1 in tizen org:

      http://download.tizen.org/iris/latest-release/openSUSE_13.1/

    1.3 $ansible-playbook base.yml site.yml -i vagrant

    1.4 check iris version in your vagrant is right:

        .. _1.4.1:

        1.4.1 open iris with browser like firefox or chrome:

            for example, my network port configuration for vagrant is 8082, my hostname is lihuan,

            then I should open http://lihuan.bj.intel.com:8082

        .. _1.4.2:

        1.4.2 check iris version:

            check if '0.2.1' in 'Currently vxxxx' at the bottom of the home page like bellow:

            .. image:: version.PNG

2. import online data to old iris

    2.1 generate online data:

        2.2.1 login to the production server

        2.2.2 $mysqldump -hhostname -uusername -ppassword dbname > 021.sql

              (the filename "021.sql" you can choose anyone you like, if you don't have permission,

              you can ask xuesong or huanhuan for help)

    2.2 change to vagrant directory

    2.3 copy 021.sql back from production server

        $scp user@servername:/xx/xxx/xx .

    2.4 $vagrant ssh -c "cat /vagrant/021.sql | mysql -uroot testdb"

    2.5 check if there is data in your iris:

        2.4.1 open iris with browser like `1.4.1`_

        2.42. check that there are gittrees, domains, subdomains in Package Database

3. upgrade iris to new version

    3.1 change repo in “host_vars/vagrant” to testing repo

        like http://download.otctools.jf.intel.com/staging/iris/archive/0.2.2/openSUSE_13.1/

    3.2 $ansible-playbook site.yml -i vagrant

        (no need to run base.xml, because we just want to upgrade iris)

    3.3 check iris version is 0.2.2 like `1.4.2`_

Feature and bug Testing
-----------------------
1. testing based on fixed bugs and new features

   Do these testing on your vagrant iris
