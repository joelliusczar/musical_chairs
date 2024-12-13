require "fileutils"
require "salad_prep"

module Provincial
	using SaladPrep::Strink

	PackageManagers = SaladPrep::Enums::PackageManagers
	
	class MCEgg < SaladPrep::Egg

		attr_reader :ices_branch

		def initialize(ices_branch:nil, **rest)
			super(**rest)
			@ices_branch = ices_branch
		end
		
		def lib
			"#{project_name_snake}_libs"
		end
		
		def lib_import
			"#{project_name_snake}_libs"
		end

		def s3_api_key(prefer_keys_file: true)
			env_find(
				"AWS_ACCESS_KEY_ID",
				/AWS_ACCESS_KEY_ID=(\w+)/,
				prefer_keys_file:
			)
		end

		def s3_secret_key(prefer_keys_file: true)
			env_find(
				"AWS_SECRET_ACCESS_KEY",
				/AWS_SECRET_ACCESS_KEY=([\w\/\+]+)/,
				prefer_keys_file:
			)
		end

		def s3_bucket_name(prefer_keys_file: true)
			env_find(
				"S3_BUCKET_NAME",
				/S3_BUCKET_NAME=([\w\-]+)/,
				prefer_keys_file:
			)
		end

		def s3_region_name(prefer_keys_file: true)
			env_find(
				"S3_REGION_NAME",
				/S3_REGION_NAME=([\w\-]+)/,
				prefer_keys_file:
			)
		end

		def s3_endpoint(prefer_keys_file: true)
			env_find(
				"AWS_ENDPOINT_URL",
				/AWS_ENDPOINT_URL=(.+)/,
				prefer_keys_file:
			)
		end

		def radio_db_user_key(prefer_keys_file: true)
			env_find(
				"MC_DB_PASS_RADIO",
				/DB_PASS_RADIO=(\w+)/,
				prefer_keys_file:
			)
		end

		def radio_log_level
			ENV["#{env_prefix}_RADIO_LOG_LEVEL"]
		end

		def ices_config_dir(abs:true)
			suffix = File.join(app_trunk, "ices_configs")
			abs_suffix(suffix, abs)
		end

		def py_modules_dir(abs:true)
			suffix = File.join(app_trunk, "pyModules")
			abs_suffix(suffix, abs)
		end

		def env_hash(prefer_keys_file: true)
			{
				**super,

				"AWS_ACCESS_KEY_ID" =>
					s3_api_key(prefer_keys_file:),

				"AWS_SECRET_ACCESS_KEY" => 
					s3_secret_key(prefer_keys_file:),

				"S3_BUCKET_NAME" =>
					s3_bucket_name(prefer_keys_file:),

				"S3_REGION_NAME" =>
					s3_region_name(prefer_keys_file:),

				"AWS_ENDPOINT_URL" =>
					s3_endpoint(prefer_keys_file:),

				"MC_DB_PASS_RADIO" =>
					radio_db_user_key(prefer_keys_file:)
			}
		end

		def local_env_hash
			{
				**super,
				"MC_ICES_CONFIGS_DIR" => ices_config_dir(abs: false),
				"MC_PY_MODULE_DIR" => py_modules_dir(abs: false)
			}
		end

		def generate_initial_keys_file
			super do |file|
			end
		end

		def server_env_check_recommended
			result = super
			result.push("ices_branch") if ices_branch.zero?
			result
		end

		def server_env_check_required
			result = super
			result.push("s3_api_key") if s3_api_key(prefer_keys_file: false).zero?
			result.push("s3_secret_key") \
				if s3_secret_key(prefer_keys_file: false).zero?
			result.push("s3_bucket_name") \
				if s3_bucket_name(prefer_keys_file: false).zero?
			result.push("s3_region_name") \
				if s3_region_name(prefer_keys_file: false).zero?
			result.push("s3_endpoint") if s3_endpoint(prefer_keys_file: false).zero?
			result.push("radio_db_user_key") \
				if radio_db_user_key(prefer_keys_file: false).zero?
			result
		end

		def deployment_env_check_recommended
			result = super
			result.push("radio_log_level") if radio_log_level.zero?
			result
		end

		def deployment_env_check_required
			result = super
			result.push("s3_api_key") if s3_api_key.zero?
			result.push("s3_secret_key") if s3_secret_key.zero?
			result.push("s3_bucket_name") if s3_bucket_name.zero?
			result.push("s3_region_name") if s3_region_name.zero?
			result.push("s3_endpoint") if s3_endpoint.zero?
			result.push("radio_db_user_key") if radio_db_user_key.zero?
			result
		end

		def dev_env_check_required
			result = super
			result.push("s3_api_key") if s3_api_key(prefer_keys_file: false).zero?
			result.push("s3_secret_key") \
				if s3_secret_key(prefer_keys_file: false).zero?
			result.push("s3_bucket_name") \
				if s3_bucket_name(prefer_keys_file: false).zero?
			result.push("s3_region_name") \
				if s3_region_name(prefer_keys_file: false).zero?
			result.push("s3_endpoint") if s3_endpoint(prefer_keys_file: false).zero?
			result.push("radio_db_user_key") \
				if radio_db_user_key(prefer_keys_file: false).zero?
			result
		end
		
	end

	class MCBrickStack < SaladPrep::BrickStack
		def setup_app_directories
			super
			FileUtils.mkdir_p(@egg.ices_config_dir)
			FileUtils.mkdir_p(@egg.py_modules_dir)
		end

	end

	class IcesInstaller

		attr_accessor :clean

		def initialize(
			egg:,
			monty:,
			radio_launcher:,
			min_ices_version:,
			ices_branch: nil
		)
			@egg = egg
			@monty = monty
			@radio_launcher = radio_launcher
			@min_ices_version = min_ices_version
			@ices_branch = ices_branch
			@clean = false
		end

		def install_dependencies
			if ! system("aclocal --version 2>/dev/null") 
				SaladPrep::BoxBox.install_package("automake")
			end
	
			case Gem::Platform::local.os
			when SaladPrep::Enums::BoxOSes::MACOS
				SaladPrep::BoxBox.install_if_missing("libtool")
				SaladPrep::BoxBox.install_if_missing("pkg-config")
				SaladPrep::BoxBox.install_if_missing("libshout")
			when SaladPrep::Enums::BoxOSes::LINUX
				if SaladPrep::BoxBox.is_installed?(
					SaladPrep::Enums::PackageManagers::APTGET
				) then
					SaladPrep::BoxBox.install_if_missing("libtool-bin")
				end
				SaladPrep::BoxBox.install_if_missing("build-essential")
				SaladPrep::BoxBox.install_if_missing("libxml2-dev")
				SaladPrep::BoxBox.install_if_missing("libogg-dev")
				SaladPrep::BoxBox.install_if_missing("libvorbis-dev")
				SaladPrep::BoxBox.install_if_missing("libshout3-dev")
				SaladPrep::BoxBox.install_if_missing("libmp3lame-dev")
				SaladPrep::BoxBox.install_if_missing("libflac-dev")
				SaladPrep::BoxBox.install_if_missing("libfaad-dev")
				SaladPrep::BoxBox.install_if_missing("libperl-dev")
				py_version = @monty.python_version
				if (py_version.take(2).map(&:to_i) <=> [3, 12]) < 0
					SaladPrep::BoxBox.install_if_missing("python3-distutils")
				end
				SaladPrep::BoxBox.install_if_missing(
					"python#{py_version[0]}.#{py_version[1]}-dev"
				)
			else
				raise "OS is not setup"
			end
		end

		def ices_command
			"#{@egg.env_prefix}-ices".downcase
		end

		def ices_version
			begin
				`#{ices_command} -V`.split("\n").first[/[\d\.]+/].split(".")
			rescue RuntimeError
				[-1,-1-1]
			end
		end

		def is_installed_version_good?
			min_version = @min_ices_version.split(".").take(3).map(&:to_i)
			installed_version = ices_version.take(3).map(&:to_i)
			(installed_version <=> min_version) > -1
		end

		def install_ices()
			if ! SaladPrep::BoxBox.is_installed?(ices_command) \
				|| ! is_installed_version_good?
			then
				install_ices_unchecked()
			end
		end

		def install_ices_unchecked()
			@radio_launcher.shutdown_all_stations
			install_dependencies
			ices_build_dir = File.join(@egg.build_dir, "ices")
			FileUtils.rm_rf(ices_build_dir)
			Dir.chdir(@egg.build_dir) do 
				system(
					"git clone https://github.com/joelliusczar/ices0.git ices",
					exception: true
				)
				Dir.chdir("ices") do
					if @ices_branch.populated?
						system(
							"git","checkout", "-t", "origin/#{@ices_branch}",
							exception: true
						)
					end
					system(
						"aclocal && autoreconf -fi && automake --add-missing",
						exception: true
					)
					python_path = SaladPrep::BoxBox.which(@monty.python_command).first
					system(
						"./configure",
						"--prefix=#{@egg.bin_parent_dir(abs: true)}",
						"--with-python=#{python_path}",
						"--with-moddir=#{@egg.py_modules_dir(abs: true)}",
						"--program-prefix=#{@egg.env_prefix.downcase}-",
						exception: true
					)
					system("make && make install", exception: true)
				end 
				if @clean
					FileUtils.rm_r(ices_build_dir)
				end
			end
		end

	end

	class MCInstallion < SaladPrep::Installion

		def initialize(
			egg:,
			monty:,
			ices_installer:,
			radio_launcher:
		)
			super(egg)
			@monty = monty
			@ices_installer = ices_installer
			@radio_launcher = radio_launcher
		end

		def install_dependencies
			self.class.curl
			self.class.nodejs
			self.class.python_full(@egg, @monty)
			self.class.icecast(@radio_launcher)
			@ices_installer.install_ices()
		end

		def self.icecast(radio_launcher)
			case Gem::Platform::local.os
			when SaladPrep::Enums::BoxOSes::LINUX
				if SaladPrep::BoxBox.uses_aptget?
					if ! SaladPrep::BoxBox.is_installed?("icecast2")
						SaladPrep::BoxBox.install_package("icecast2")
						radio_launcher.setup_icecast_confs
					end
				elsif SaladPrep::BoxBox.is_installed?(PackageManagers::PACMAN)
					if ! SaladPrep::BoxBox.is_installed?("icecast")
						SaladPrep::BoxBox.install_package("icecast", input: "no")
						radio_launcher.setup_icecast_confs
					end
				else
					raise "distro not configured for installing icecast"
				end
			else
				raise "OS not configured for installing icecast"
			end
		end
		
	end

	class RadioLauncher

		def initialize(
			egg:,
			monty:,
			brick_stack:,
			dbass:
		)
			@egg = egg
			@monty = monty
			@brick_stack = brick_stack
			@dbass = dbass
		end


		def icecast_name
			if SaladPrep::BoxBox.is_installed(
				SaladPrep::Enums::PackageManagers::APTGET
			) then
				"icecast2"
			elsif SaladPrep::BoxBox.is_installed(
				SaladPrep::Enums::PackageManagers::PACMAN
			) then
				"icecast"
			end
		end

		def sync_station_module
			src = File.join(
				@egg.template_dest,
				socket_template.py
			)
			dest = File.join(
				@egg.py_modules_dir(abs: false),
				"station.py"
			)
			FileUtils.cp(src, dest)
		end

		def start_icecast_service(service_name)
			case Gem::Platform::local.os
				when SaladPrep::Enums::BoxOSes::LINUX
					if ! system("systemctl", "is-active", "--quiet", service_name)
						system("systemctl", "enable", service_name)
						system("systemctl", "start", service_name)
					end
				else
					raise "OS is not configured icecast"
			end
		end

		def icecast_conf(service_name)
			case Gem::Platform::local.os
			when SaladPrep::Enums::BoxOSes::LINUX
				IO.popen(["systemctl", "status", service_name]) {|p| p.read }
					.split("\n")
					.filter {|l| l =~ %r{/usr/bin/icecast2}}
					.first
					.split[-1]
			when SaladPrep::Enums::BoxOSes::MACOS
				#we don't have icecast on the mac anyway so we'll just return the
				#source code location
				File.join(
					@egg.templates_src,
					"icecast.xml"
				)
			else
				raise "OS is not configured icecast"
			end
		end

		def update_icecast_conf(
			icecast_conf_path,
			src_pass,
			relay_pass,
			admin_pass
		)
			FileHerder::update_in_place(icecast_conf_path) do |l|
				if /source-password/ =~ l
					l.gsub(/>\w*/,">#{src_pass}")
				elsif /relay-password/ =~ l
					l.gsub(/>\w*/,">#{relay_pass}")
				elsif /admin-password/ =~ l
					l.gsub(/>\w*/,">#{admin_pass}")
				elsif /<bind-address>/ =~ l
					l.gsub(%r{^([ \t]*)<.*},"\1<bind-address>::</bind-address>")
				else
					l
				end
			end
		end

		def update_ices_config(conf, src_pass)
			FileHerder::update_in_place(conf) do |l|
				if /Password/ =~ l
					l.gsub(/>\w*/,">#{src_pass}")
				else
					l
				end
			end
		end

		def update_all_ices_confs(src_pass)
			Dir["#{@egg.ices_config_dir}/*.conf"].each do |conf|
				update_ices_config(conf, src_pass)
			end
		end

		def setup_icecast_confs
			name = icecast_name
			start_icecast_service(name)
			icecast_conf_path = get_icecast_conf(name)
			src_pass = SecureRandom.alphanumeric(32)
			update_icecast_conf(
				icecast_conf_path,
				src_pass,
				src_pass,
				src_pass
			)
			update_all_ices_confs(src_pass)
			system("systemctl", "restart", name, exception: true)
		end

		def setup_radio
			shutdown_all_stations
			@monty.sync_requirement_list
			@brick_stack.sync_utility_scripts
			@monty.create_py_env_in_app_trunk
			FileHerder.copy_dir(
				@egg.templates_src,
				@egg.template_dest
			)
			sync_station_module
			@dbass.setup_db
			setup_icecast_confs
		end

		def shutdown_all_stations
			if ! File.exist?(@monty.py_env_activate_path)
				puts("python env not setup, so no stations to shut down")
				return
			end
			script = <<~CODE
				try:
					from musical_chairs_libs.station_service import StationService
					from sqlalchemy.exc import OperationalError
					try:
						stationService = StationService()
						stationService.end_all_stations()
					except OperationalError as ex:
						print("Could not the shutdown operation."
						" Assuming that they are already down.")
				except ModuleNotFoundError:
					print("Could not import something")
				print("Done")
			CODE
			@monty.run_python_script(script)
		end

		def show_icecast_log
			script = <<~CODE
				from musical_chairs_libs.services import ProcessService
				from musical_chairs_libs.services import EnvManager
				icecastConfLocation = ProcessService.get_icecast_conf_location()
				logdir = EnvManager.read_config_value(
					icecastConfLocation,
					"logdir"
				)
				errorlog = EnvManager.read_config_value(
					icecastConfLocation,
					"errorlog"
				)
				print(f"{logdir}/{errorlog}")
			CODE
			@monty.run_python_script(script)
		end

		def show_icecast_log
			script = <<~CODE
				from musical_chairs_libs.services import (
					StationService,
					QueueService,
					EnvManager,
				)
				from datetime import datetime, timedelta, timezone

				envManager = EnvManager()
				conn = envManager.get_configured_janitor_connection(
					"musical_chairs_db"
				)
				try:
					stationService = StationService(conn)
					queueService = QueueService(conn, stationService)
					stations = list(stationService.get_stations())
					dt = datetime.now(timezone.utc)
					cutoffDate = (dt - timedelta(days=7)).timestamp()
					print(f"Cut off date: {cutoffDate}")
					for station in stations:
						result = queueService.squish_station_history(station.id, cutoffDate)
						print(f"Added count: {result[0]}")
						print(f"Updated count: {result[1]}")
						print(f"Deleted count: {result[2]}")

				finally:
					conn.close()

			CODE
			@monty.run_python_script(script)
		end

		def show_ices_station_log
			script = <<~CODE
				from musical_chairs_libs.services import EnvManager
				logdir = EnvManager.read_config_value(
					"${logName}",
					"BaseDirectory"
				)
				print(f"{logdir}/ices.log")
			CODE
			@monty.run_python_script(script)
		end

		def regen_station_configs
			script = <<~CODE
				from musical_chairs_libs.services import (
					StationService,
					EnvManager,
					TemplateService
				)

				envManager = EnvManager()
				conn = envManager.get_configured_api_connection("musical_chairs_db")
				try:
					stationService = StationService(conn)
					templateService = TemplateService()
					stations = list(stationService.get_stations())
					for station in stations:
						templateService.create_station_files(
							0,
							station.name,
							station.displayname,
							station.owner.username
						)

				finally:
					conn.close()

			CODE
			@monty.run_python_script(script)
		end

	end

	class MCDbAss < SaladPrep::MyAss

		def initialize(egg, monty)
			super(egg)
			@monty = monty
		end

		def setup_db
			replace_sql_scripts
			root_hash=`mysql -srN -e \
				"SELECT password FROM mysql.user WHERE user = 'root' LIMIT 1" 2>&1
			`
			if root_hash.zero? || root_hash == "invalid"
				SaladPrep::MyAssRoot.set_db_root_initial_password(@egg.db_setup_key)
			end
			script = <<~CODE
				from musical_chairs_libs.services import (
					setup_database
				)
				dbName="musical_chairs_db"
				setup_database(dbName)
			CODE
			@monty.run_python_script(script)
		end

		def teardown_db
			script = <<~CODE
				from musical_chairs_libs.services import (
					DbRootConnectionService,
					DbOwnerConnectionService
				)

				with DbRootConnectionService() as rootConnService:
					rootConnService.drop_all_users()
					rootConnService.drop_database("musical chairs_db")
			CODE
			@monty.run_python_script(script)
		end

	end

	module SaladPrep::Enums::SetupLvls
		RADIO = "radio"
		ICES = "ices"
	end

	class MCRemote < SaladPrep::Remote
		def ruby_script(setup_lvl, current_branch)
			ruby_content = SaladPrep::Resorcerer.ruby_template_compile(
				setup_lvl:setup_lvl,
				current_branch: current_branch
			)
			dev_ops_path = File.join(
				@egg.repo_path,
				"dev_ops",
				"dev_ops.rb"
			)
			File.open(dev_ops_path).read ^ ruby_content
		end
	
	end
	
	class MCFarPort < SaladPrep::FarPort

		def initialize(
			radio_launcher:,
			ices_installer:,
			**rest
		)
			super(**rest)
			@radio_launcher = radio_launcher
			@ices_installer =  ices_installer
		end

		def remote_setup_path(setup_lvl)
			super(setup_lvl) do 
				if setup_lvl == saladPrep::Enums::SetupLvls.RADIO
					@radio_launcher.setup_radio
				elsif setup_lvl == saladPrep::Enums::SetupLvls.ICES
					@ices_installer.install_ices_unchecked()
				end
			end
		end

	end

	class MCBinstallion < SaladPrep::Binstallion

		def install_bins
			super
			install_py_env_if_needed
		end

	end
	
	
	
	@egg = MCEgg.new(
		project_name_0: "musical chairs",
		local_repo_path: ENV["MC_LOCAL_REPO_DIR"],
		repo_url: ENV["MC_REPO_URL"],
		env_prefix: "MC",
		url_base: "musicalchairs",
		tld: "radio.fm",
		db_owner_name: "mc_owner"
	)

	generated_file_dir = File.join(@egg.lib_src, "dtos_and_utilities")
	
	
	@brick_stack = MCBrickStack.new(@egg)
	@monty = SaladPrep::Monty.new(
		@egg, 
		generated_file_dir: generated_file_dir
	)
	@dbass = MCDbAss.new(@egg, @monty)
	@w_spoon = SaladPrep::WSpoon.new(@egg, SaladPrep::Resorcerer)
	@api_launcher = SaladPrep::PyAPILauncher.new(
		egg: @egg,
		dbass: @dbass,
		w_spoon: @w_spoon,
		monty: @monty
	)
	@client_launcher = SaladPrep::ClientLauncher.new(@egg)
	@radio_launcher = RadioLauncher.new(
		egg: @egg,
		monty: @monty,
		brick_stack: @brick_stack,
		dbass: @dbass
	)
	@ices_installer = IcesInstaller.new(
		egg: @egg,
		monty: @monty,
		radio_launcher: @radio_launcher,
		min_ices_version: "0.6.1",
		ices_branch: "restructure-logging"
	)
	@installer = MCInstallion.new(
		egg: @egg,
		monty: @monty,
		ices_installer: @ices_installer,
		radio_launcher: @radio_launcher
	)
	@far_port = MCFarPort.new(
		egg: @egg,
		api_launcher: @api_launcher,
		client_launcher: @client_launcher,
		radio_launcher: @radio_launcher,
		installer: @installer,
		ices_installer: @ices_installer
	)
	@binstallion = MCBinstallion.new(
		@egg,
		File.join(
			@egg.repo_path,
			"dev_ops",
			"dev_ops.rb"
		)
	)

	def self.egg
		@egg
	end

	def self.brick_stack
		@brick_stack
	end

	def self.dbass
		@dbass
	end

	def self.w_spoon
		@w_spoon
	end
	
	def self.monty
		@monty
	end

	def self.api_launcher
		@api_launcher
	end

	def self.client_launcher
		@client_launcher
	end

	def self.radio_launcher
		@radio_launcher
	end

	def self.far_port
		@far_port
	end

	def self.binstallion
		@binstallion
	end

end