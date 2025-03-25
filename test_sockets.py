import socket
import select 
import sys
import asyncio

IP_address = "10.239.109.169" #CHANGE TO IP ADDRESS
port = int(input("Enter the port number: "))


class Node: 
        def __init__(self, ip,port): 
                self.ip = ip
                self.port = port # set port number
                self.server = None
                self.clients = set() # set a list of clients 
        async def start_server(self): 
                self.server = await asyncio.start_server(self.handle_client, self.ip, self.port)
                print(f"server listening on {self.ip}:{self.port}")
                async with self.server: 
                        await self.server.serve_forever() 
        async def handle_client(self,reader,writer): 
                addr = writer.get_extra_info('peername')
                print(f"{addr} connected")
                self.clients.add(writer)
                try: 
                        while True:
                                data = await reader.read(100)
                                message = data.decode()
                                if message: 
                                        print(f"<{addr}> {message}")
                                        await self.broadcast(message,writer)
                                else:
                                        break
                except: 
                        pass
                finally: 
                        self.clients.remove(writer)
                        writer.close()
                        await writer.wait_closed()
        async def broadcast(self,message, writer): 
                for client in self.clients: # for each client 
                        if client != writer: 
                                client.write(message.encode())
                                await client.drain()
        async def connect_to_peer(self, peer_ip, peer_port): # pass ip address and port number to connect to other peers
            reader, writer = await asyncio.open_connection(peer_ip, peer_port)
            self.clients.add(writer)
            print(f"Connected to {peer_ip}: {peer_port}")
            return reader, writer
        async def send_message(self, writer, message):
                writer.write(message.encode())
                await writer.drain()
async def main(): 
        node = Node(IP_address, port)
         # Start the server in the background
        asyncio.create_task(node.start_server())


        #connecting to peer
        connect = input("Do you want to connect to a peer? (y/n): ")
        if connect == "y": 
                peer_ip= input("Enter peer IP: ")
                peer_port = int(input("Enter peer port: "))
                writer = await node.connect_to_peer( peer_ip, peer_port) 

                if writer: 
                        while True: 
                                message = input("Message to send (or type quit): ")
                                if message.lower() == "quit":  
                                        print("Exiting...")
                                        writer.close()
                                        exit
                                
                                await writer.send_message(writer,message)

asyncio.run(main())
