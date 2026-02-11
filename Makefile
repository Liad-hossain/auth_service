# Load environment variables from .env file
-include .env
export

## help: print this help message
.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'


.PHONY: get_migrate
get-migrate:
	curl -L https://github.com/golang-migrate/migrate/releases/download/v4.16.2/migrate.darwin-arm64.tar.gz | tar xz -- migrate

.PHONY: get_migrate_linux
get-migrate-linux:
	curl -L https://github.com/golang-migrate/migrate/releases/download/v4.16.2/migrate.linux-amd64.tar.gz | tar xvz -- migrate

## migrations-new name=$1: create a new database migration
.PHONY: migrations-new
migrations-new:
	./migrate create -seq -ext=.sql -dir=./src/db/migrations ${name}
# ./migrate create -ext sql -dir assets/migrations -seq ${name}

## migrations-up: apply all up database migrations
## migrations-up number=N: apply next N number of database migrations
.PHONY: migrations-up
migrations-up:
	./migrate -path=./src/db/migrations -database="${MASTER_DATABASE_URL}" up ${number}

## migrations-down: apply all down database migrations
## migrations-down number=N: apply previous N number of down database migrations
.PHONY: migrations-down
migrations-down:
	./migrate -path=./src/db/migrations -database="${MASTER_DATABASE_URL}" down ${number}

## migrations-goto version=$1: migrate to a specific version number
.PHONY: migrations-goto
migrations-goto:
	./migrate -path=./src/db/migrations -database="${MASTER_DATABASE_URL}" goto ${version}

## migrations-force version=$1: force database migration
.PHONY: migrations-force
migrations-force:
	./migrate -path=./src/db/migrations -database="${MASTER_DATABASE_URL}" force ${version}


## migrations-version: print the current in-use migration version
.PHONY: migrations-version
migrations-version:
	./migrate -path=./src/db/migrations -database="${MASTER_DATABASE_URL}" version

## migrations-drop: drop full database
.PHONY: migrations-drop
migrations-drop:
	./migrate -path=./src/db/migrations -database="${MASTER_DATABASE_URL}" drop

# build build the project
build:
	docker compose -f ./deploy/docker-compose.yml build

run:
	docker compose -f ./deploy/docker-compose.yml up --build


clean:
	docker compose -f ./deploy/docker-compose.yml down --rmi all
