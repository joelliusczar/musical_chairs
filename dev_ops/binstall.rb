require_relative "./dev_ops"

puts("install")

Provincial.binstallion.install_bins({ "--dev" => "true"})

puts("Done")
