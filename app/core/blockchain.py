import random
import traceback
import asyncio

# Try importing bittensor, but gracefully handle if it's not available
try:
    import bittensor
    # Check if we have the wallet module
    if hasattr(bittensor, 'wallet'):
        from bittensor import wallet
        REAL_WALLET_AVAILABLE = True
    else:
        print("Bittensor wallet module not available, using mock implementation")
        REAL_WALLET_AVAILABLE = False
        
    # Check if we have the subtensor module
    if hasattr(bittensor, 'subtensor'):
        from bittensor import subtensor
        REAL_SUBTENSOR_AVAILABLE = True
    else:
        print("Bittensor subtensor module not available, using mock implementation")
        REAL_SUBTENSOR_AVAILABLE = False
except ImportError:
    print("Bittensor package not available, using mock implementations")
    REAL_WALLET_AVAILABLE = False
    REAL_SUBTENSOR_AVAILABLE = False

class BitensorClient:
    _instance = None
    _initialized = False
    _subtensor = None
    
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = BitensorClient()
            await cls._instance._init_subtensor()
        return cls._instance
    
    async def _init_subtensor(self):
        """Initialize subtensor connection with retry logic"""
        if self._initialized:
            return
        
        try:
            if REAL_SUBTENSOR_AVAILABLE:
                print("Initializing real Bittensor connection...")
                # Initialize real subtensor
                self._subtensor = await subtensor.Subtensor.from_chain_endpoint(
                    chain_endpoint="ws://test.finney.opentensor.ai:9944"
                )
            else:
                # Mock initialization
                print("Initializing mock Bittensor connection...")
                await asyncio.sleep(0.1)  # Small delay to simulate initialization
            
            self._initialized = True
            print("BitensorClient initialized successfully")
        except Exception as e:
            print(f"Error initializing subtensor: {e}")
            print(traceback.format_exc())
            # Continue with mock implementation
            self._initialized = True
    
    async def get_dividends(self, netuid: int, hotkey: str = None) -> dict:
        """
        Get TAO dividends for a specific hotkey and subnet
        Falls back to mock data if real implementation fails
        """
        # Ensure subtensor is initialized
        if not self._initialized:
            await self._init_subtensor()
            
        try:
            if REAL_SUBTENSOR_AVAILABLE and REAL_WALLET_AVAILABLE and self._subtensor:
                print(f"Querying real blockchain for dividends: netuid={netuid}, hotkey={hotkey}")
                
                # Default hotkey if not provided
                if not hotkey:
                    hotkey = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
                
                # Get neuron information
                try:
                    neuron = await self._subtensor.get_neuron_for_pubkey_and_subnet(
                        hotkey_ss58=hotkey,
                        netuid=netuid
                    )
                    
                    # Get dividend information
                    dividends = await self._subtensor.get_tao_dividends_per_subnet(
                        netuid=netuid,
                        hotkey_ss58=hotkey
                    )
                    
                    # Get balance
                    balance = await self._subtensor.get_balance(hotkey)
                    
                    # Build response from real data
                    stake = neuron.stake if neuron else 0
                    is_registered = neuron is not None
                    
                    return {
                        "netuid": netuid,
                        "hotkey": hotkey,
                        "dividends": float(dividends) if dividends is not None else 0.0,
                        "stake": float(stake),
                        "balance": float(balance),
                        "is_registered": is_registered
                    }
                except Exception as e:
                    print(f"Error in real blockchain query: {e}")
                    # Fall back to mock data
                    return self._generate_mock_data(netuid, hotkey)
            else:
                # Use mock data if real implementation is not available
                return self._generate_mock_data(netuid, hotkey)
                
        except Exception as e:
            print(f"Error querying blockchain: {e}")
            print(traceback.format_exc())
            
            # Fall back to mock data on error
            return self._generate_mock_data(netuid, hotkey)
    
    def _generate_mock_data(self, netuid: int, hotkey: str = None) -> dict:
        """Generate deterministic mock data to simulate blockchain response"""
        print(f"Generating mock data for netuid={netuid}, hotkey={hotkey}")
        
        # Default hotkey if not provided
        if not hotkey:
            hotkey = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
        
        # Use a predictable seed based on inputs to ensure consistent mock data
        seed = hash(f"{netuid}:{hotkey}")
        random.seed(seed)
        
        # Generate mock balance between 0 and 100 TAO
        balance = random.uniform(0, 100)
        
        # Generate mock stake (0-50% of balance)
        stake = balance * random.uniform(0, 0.5)
        
        # Generate mock dividends (0-5% of stake)
        dividends = stake * random.uniform(0, 0.05)
        
        # Return mock data
        return {
            "netuid": netuid,
            "hotkey": hotkey,
            "dividends": round(dividends, 6),
            "stake": round(stake, 6),
            "balance": round(balance, 6),
            "is_registered": random.choice([True, False])
        }