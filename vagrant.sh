#!/bin/sh
function user_run { runuser -l vagrant -c "$*"; }

echo "Installing packages.."
pacman -Sy
pacman -S --needed --noconfirm gcc ruby python2 python2-pip mongodb

echo "Installing python packages.."
pip2 install -r /www-src/requirements.txt

echo "Installing ruby packages.."
gem install --no-user-install sass

echo "Checking for GEM bin.."
if ! grep -q "\`ruby -e 'puts Gem.user_dir'\`/bin" /home/vagrant/.bashrc ; then
    echo "GEM bin is not in path, adding to .bashrc"
    echo "PATH=\"\`ruby -e 'puts Gem.user_dir'\`/bin:\$PATH\"" | user_run tee -a /home/vagrant/.bashrc
fi

echo "Setting up mongo.."
sed -i "s/^\(bind_ip\s*=\s*\).*$/\10\.0\.0\.0/" /etc/mongodb.conf
systemctl enable mongodb
systemctl start mongodb

echo "Attempting to create convenience symlink.."
user_run ln -s /www-src/ /home/vagrant/

echo "Attempting to bootstrap local_config.."
user_run cp -n /www-src/config/local_config.py.default /www-src/config/local_config.py

echo "====== Please set a SECRET_KEY in config/local_config.py before starting ======"
echo "====== Run 'vagrant ssh' to get a shell ======"
