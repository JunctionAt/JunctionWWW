
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "arch64-min"
    config.vm.box_url = "http://downloads.sourceforge.net/project/flowboard-vagrant-boxes/arch64-2013-07-26-minimal.box"
    config.vm.hostname = "junction.vagrant.webdev"

    config.vm.synced_folder ".", "/www-src"
    config.vm.network "forwarded_port", guest: 8080, host: 8080
    config.vm.network "forwarded_port", guest: 27017, host: 8081

    config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--memory", "512"]
        vb.customize ["modifyvm", :id, "--cpus", 1]

        vb.customize ["modifyvm", :id, "--usb", "off"]
        vb.customize ["modifyvm", :id, "--usbehci", "off"]
    end

    config.vm.provision "shell", path: "vagrant.sh"

end
