.PHONY: all run clean

all: beepboop

beepboop: main.go
	go build -gcflags '-l' -o beepboop .

run:
	FLAG="PP{test-flag}" ./beepboop

clean:
	rm -f ./beepboop
