git fetch
git checkout main
git status

$confirmation = Read-Host "All above local changes will be deleted. Proceed? [y/n]"

if ($confirmation -eq 'n') {exit}
git clean -f -d
git reset --hard origin
