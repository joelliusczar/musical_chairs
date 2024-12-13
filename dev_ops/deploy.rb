require "salad_prep"
require_relative "./dev_ops"
using SaladPrep::Strink


test_honcho = SaladPrep::PyTestHoncho.new(
	egg: Provincial.egg,
	dbass: Provincial.dbass,
	brick_stack: Provincial.brick_stack,
	monty: Provincial.monty
)

remote = Provincial::MCRemote.new(Provincial.egg, test_honcho)

puts(ARGV)

setuplvl = ""
ARGV.each do |arg|
	if arg.start_with?("setuplvl=")
		setuplvl = arg.split("=").map(&:chomp).last
	end
end
ARGV.clear

# Provincial.egg.run_test_block do
# 	puts(Provincial.egg.ices_config_dir)
# end

# remote.connect_root



# connect_root
# exec(
# 	"ssh",
# 	"-ti",
# 	Provincial.egg.ssh_id_file,
# 	"root@#{Provincial.egg.ssh_address}",
# 	"bash -l",
# )



remote.deploy(setuplvl, update_salad_prep: true, print_env: true)