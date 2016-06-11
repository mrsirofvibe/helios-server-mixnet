# -*- coding: utf-8 -*-
#
# ============================================================================
# About this file:
# ============================================================================
#
#  PartialDecryption.py : 
#  A partial decryption generated in a threshold encryption scheme.
#
#  Each trustee generates a partial decryption using their threshold private 
#  key, and then k=threshold distinct partial decryptions can be combined 
#  using ThresholdDecryptionCombinator into the decrypted plaintext.
#
#  Part of the PloneVote cryptographic library (PloneVoteCryptoLib)
#
#  Originally written by: Lazaro Clapp
#
# ============================================================================
# LICENSE (MIT License - http://www.opensource.org/licenses/mit-license):
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ============================================================================

class PartialDecryptionBlockProof:
	"""
	A machine verifiable Zero-Knowledge proof for a block of partial decryption.
	
	Each partial decryption block proof is a Zero-Knowledge Discrete Logarithm 
	Equality Test, proving that g^{2P(j)} and block = gamma^{2P(j)} have indeed 
	the same exponent. That is, that:
	
		log_{g}(g^{2P(j)}) == log_{gamma}(block^2)
		
	Proving that block = gamma^{P(j)}, without revealing P(j), the threshold  
	private key used for the partial decryption.
	
	See (TODO: Add reference)
	
	NOTE: The values for the attributes listed below are intended to be 
	informative and represent what a CORRECT proof of partial decryption should 
	contain. However, this class is only used to store the triplet of values 
	for the proof and does not enforce their form. A proof must still be 
	checked for correctness before accepting the corresponding block of partial 
	decryption. Which is done inside PloneVoteCryptoLib in 
	ThresholdDecryptionCombinator.add_partial_decryption(...). 
	
	Attributes:
		a::long	-- g^{s} mod p for some random s in Z_{q}
		b::long -- gamma^{s} mod p for the same s
		t::long -- t = s + 2P(j)*c mod p (where c is a challenge generated by 
					hashing a, b, g^{2P(j)} and block together. 
	"""
	
	def __init__(self, a, b, t):
		"""
		Creates a new PartialDecryptionBlockProof.
		
		Arguments:
			(See class attributes and note in the class documentation)
		"""
		self.a = a
		self.b = b
		self.t = t


class PartialDecryptionBlock:
	"""
	Represents an nbits block of partial decryption.
	
	This class includes the proof of partial decryption.
	
	Attributes:
		value::long	-- The nbits block of partial decryption. Where nbits is 
					   the size in bits of the cryptosystem/public key used to 
					   encrypt the ciphertext of which this is a block of 
					   partial decryption.
		proof::PartialDecryptionBlockProof -- The corresponding proof of 
											  partial decryption.
	"""
	
	def __init__(self, value, proof):
		"""
		Creates a new PartialDecryptionBlock.
		
		Arguments:
			(See class attributes and note in the class documentation)
		"""
		self.value = value
		self.proof = proof
	


class PartialDecryption:
	"""
	A partial decryption generated in a threshold encryption scheme.
	
	To decrypt a threshold encrypted ciphertext with n trustees and a threshold 
	of k, each decrypting trustee must generate a partial decryption from the 
	ciphertext using its threshold private key. Any k of this partial 
	decryptions can then be combined using ThresholdDecryptionCombinator to 
	retrieve the original plaintext.
	
	Attributes:
		nbits::int	-- Size in bits of the cryptosystem/public key used to 
					   encrypt the ciphertext of which this is a partial 
					   decryption.
	"""
	
	def __getitem__(self, i):
		"""
		Makes this object indexable.
		
		Returns:
			block::PartialDecryptionBlock	-- 
						 	Returns the ith nbits block of partial decryption. 
						 	This blocks should only be used by select classes 
						 	within PloneVoteCryptoLib, and not from outside 
						 	classes.
		"""
		return self._blocks[i]
	
	def get_length(self):
		"""
		Get the length of this partial decryption in blocks.
		"""
		return len(self._blocks)
		
	def __init__(self, nbits):
		"""
		Create an empty partial decryption object.
		
		This constructor is not intended to be called directly from outside 
		PloneVoteCryptoLib, instead, consider using 
		ThresholdPrivateKey.generate_partial_decryption()
		
		Arguments:
			nbits::int	-- Size in bits of the cryptosystem/public key used to 
					   encrypt the ciphertext of which this is a partial 
					   decryption.
		"""
		self.nbits = nbits
		self._blocks = []
		
	def add_partial_decryption_block(self, block):
		"""
		Add an nbits block of partial decryption.
		
		This method is not intended to be called directly from outside 
		PloneVoteCryptoLib, instead, consider using 
		ThresholdPrivateKey.generate_partial_decryption()
		
		Arguments:
			block::PartialDecryptionBlock	-- 
						   A block of partial decryption information. Each 
						   block corresponds to an nbits block of the original 
						   plaintext. One can also see it as corresponding to a 
						   (gamma, delta) pair of the ciphertext.
						   Blocks each should include a proof of partial 
						   decryption.
		"""
		self._blocks.append(block)
		
