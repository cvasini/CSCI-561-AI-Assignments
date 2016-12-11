import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;
public class homework10cases {
	private static long startTime = System.currentTimeMillis();
	static int sizeOfBoard;
	static int depth;
	static String algo;
	static String youPlay;
	static String maxPlayer;
	static String minPlayer;
	static int[][] cellValues;
	static String[][] origBoardState;
	public static void main(String [] args) throws IOException {
		int nthInput = 0;
		for(nthInput = 0; nthInput<=9; nthInput++) {
			List<String> lines = Files.readAllLines(Paths.get("Test cases/testcases-10/INPUT", "input"+Integer.toString(nthInput)+".txt"));
			sizeOfBoard = Integer.parseInt(lines.get(0));
			cellValues = new int[sizeOfBoard][sizeOfBoard];
			origBoardState = new String[sizeOfBoard][sizeOfBoard];
			algo = lines.get(1);
			youPlay = lines.get(2);
			depth = Integer.parseInt(lines.get(3));
			if (youPlay.equals("X")) {
				maxPlayer = "X";
				minPlayer = "O";
			} else {
				maxPlayer = "O";
				minPlayer = "X";
			}
			//create cell values array
			int i, j, k, l;
			for(i = 4; i<=(3 + sizeOfBoard);i++) {
				String[] cellVal = lines.get(i).split(" ");
				for(j = 0; j< sizeOfBoard;j++){
					cellValues[i - 4][j] = Integer.parseInt(cellVal[j]);
				}
			}
			//create board state
			for(k = 4 + sizeOfBoard; k<=(3 + 2*sizeOfBoard);k++) {
				char[] boardSt = lines.get(k).toCharArray();
				for(l = 0; l< sizeOfBoard;l++){
					origBoardState[k-(4 + sizeOfBoard)][l] = Character.toString(boardSt[l]);
				}
			}
			//alphabet lookup
			LinkedHashMap<Integer, String> lookUpAlphabet = new LinkedHashMap<Integer, String>();
			String [] alphabets = {"A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"};
			for(i = 0; i< 26; i++) {
				lookUpAlphabet.put(i , alphabets[i]);
			}
			LinkedHashMap<String, Object> answerMove = new LinkedHashMap<String, Object>();
			String actualMove;
			if(algo.equals("MINIMAX")){
				answerMove = new homework10cases().minimaxDecision(origBoardState, depth, true);
			}
			else if(algo.equals("ALPHABETA")){
				answerMove = new homework10cases().alphabetaDecision(origBoardState, depth, Double.NEGATIVE_INFINITY, Double.POSITIVE_INFINITY, true);
			}
			String [] listMove = ((String) answerMove.get("bestMove")).split(" ");
			if(((String) answerMove.get("bestMove")).contains("raid") == false) {
				actualMove = lookUpAlphabet.get(Integer.parseInt(listMove[1])) + Integer.toString(Integer.parseInt(listMove[0]) + 1) + " Stake";
			}
			else{
				actualMove = lookUpAlphabet.get(Integer.parseInt(listMove[2])) + Integer.toString(Integer.parseInt(listMove[1]) + 1) + " Raid";
			}
			//create output file
			PrintWriter writer = new PrintWriter("Test cases/Output for 10 cases/output"+Integer.toString(nthInput)+".txt", "UTF-8");
			writer.print(actualMove);
			String [][] move = (String[][]) answerMove.get("bestMoveState");
			for(int i1= 0; i1<sizeOfBoard; i1++){
				writer.print("\n");
				for(int j1 = 0; j1< sizeOfBoard;j1++){
					writer.print(move[i1][j1]);
				}
			}
			writer.close();
			Path file1 = Paths.get("Test cases/Output for 10 cases/", "output"+Integer.toString(nthInput)+".txt");
			Path file2 = Paths.get("Test cases/testcases-10/OUTPUT/", "output"+Integer.toString(nthInput)+".txt");
			byte[] f1 = Files.readAllBytes(file1);
			byte[] f2 = Files.readAllBytes(file2);
			Arrays.equals(f1, f2);
			if(!Arrays.equals(f1, f2)) {
				System.out.println("Testcase "+nthInput+" failed");
			}
			if(nthInput == 9){
				System.out.println("end");
			}
			long endTime = System.currentTimeMillis();
			System.out.println(nthInput + "It took " + (endTime - startTime) + " milliseconds");
		}
	}
	//calculate game score
	public Double calcGameScore(String[][] currentBoardState) {
		Double gameScore = (double) 0;
		Double youPlayScore = (double) 0;
		Double oppoScore = (double)0;
		for(int i= 0; i<sizeOfBoard; i++){
			for(int j = 0; j< sizeOfBoard;j++){
				if(currentBoardState[i][j].equals(youPlay)) {
					youPlayScore += cellValues[i][j];
				} else if(!currentBoardState[i][j].equals(".")){
					oppoScore  += cellValues[i][j];
				}
			}
			gameScore = youPlayScore - oppoScore;
		}
		return gameScore;
	}
	//create a copy of 2D array
	public String[][] copy2DStringArray(String[][] strArray) {
		return java.util.Arrays.stream(strArray).map(el -> el.clone()).toArray($ -> strArray.clone());
	}
	//generates all possible moves based on current board state
	public LinkedHashMap<String, String[][]> generateMoves(String[][] currBoardState, String currentPlayer){
		LinkedHashMap<String, String[][]> stakeMoves = new LinkedHashMap<String, String[][]>();
		LinkedHashMap<String, String[][]> moves = new LinkedHashMap<String, String[][]>();
		LinkedHashMap<String, String[][]> raidMoves = new LinkedHashMap<String, String[][]>();
		raidMoves = new homework10cases().raidPossible(currBoardState, currentPlayer);
		for(int i= 0; i<sizeOfBoard; i++){
			for(int j = 0; j< sizeOfBoard;j++){
				if(currBoardState[i][j].equals(".")) {
					String[][] newBoardState = new homework10cases().copy2DStringArray(currBoardState);
					newBoardState[i][j] = currentPlayer;
					if(stakeMoves.get(Integer.toString(i)+" "+Integer.toString(j)) == null){
						stakeMoves.put(Integer.toString(i)+" "+Integer.toString(j), newBoardState);
					}
				}
			}
		}
		moves.putAll(stakeMoves);
		moves.putAll(raidMoves);
		return moves;
	}
	//check adjacent squares for a value
	public List<LinkedHashMap<String, Integer>> adjacentCheck(int rowPos, int colPos, String lookingFor, String[][] boardState) {
		int left = colPos - 1;
		int right = colPos + 1;
		int top = rowPos - 1;
		int bottom = rowPos + 1;
		List<LinkedHashMap<String, Integer>> positions = new ArrayList<LinkedHashMap<String, Integer>>();
		if(left >= 0 && boardState[rowPos][left].equals(lookingFor)){
			LinkedHashMap <String, Integer> pos = new LinkedHashMap<String, Integer>();
			pos.put("left", rowPos);
			pos.put("right", left);
			positions.add(pos);
		}
		if(right < sizeOfBoard && boardState[rowPos][right].equals(lookingFor)){
			LinkedHashMap <String, Integer> pos1 = new LinkedHashMap<String, Integer>();
			pos1.put("left", rowPos);
			pos1.put("right", right);
			positions.add(pos1);
		}
		if(top >= 0 && boardState[top][colPos].equals(lookingFor)) {
			LinkedHashMap <String, Integer> pos2 = new LinkedHashMap<String, Integer>();
			pos2.put("left", top);
			pos2.put("right", colPos);
			positions.add(pos2);
		}
		if(bottom < sizeOfBoard && boardState[bottom][colPos].equals(lookingFor)){
			LinkedHashMap <String, Integer> pos1 = new LinkedHashMap<String, Integer>();
			pos1.put("left", bottom);
			pos1.put("right", colPos);
			positions.add(pos1);
		}
		return positions;
	}
	//checks and raids opposition
	public LinkedHashMap<String, String[][]> raidPossible(String[][] generatedBoardState, String currentPlayer){
		List<LinkedHashMap<String, Integer>> currPlayerPositions = new ArrayList<LinkedHashMap<String, Integer>>();
		List<LinkedHashMap<String, Integer>> raidPositions = new ArrayList<LinkedHashMap<String, Integer>>();
		LinkedHashMap<String, String[][]> raidMoves = new LinkedHashMap<String, String[][]>();
		String oppoPlayer;
		if (currentPlayer.equals("X")){
			oppoPlayer = "O";
		} else {
			oppoPlayer = "X";
		}
		for(int row= 0; row<sizeOfBoard; row++){
			for(int col = 0; col< sizeOfBoard;col++){
				if(generatedBoardState[row][col].equals(".")) {
					currPlayerPositions = adjacentCheck(row, col, currentPlayer, generatedBoardState);
					if(!currPlayerPositions.isEmpty()){
						raidPositions = adjacentCheck(row, col, oppoPlayer, generatedBoardState);
						if(!raidPositions.isEmpty()){
							String[][] newBoardState = new homework().copy2DStringArray(generatedBoardState);
							for(int j=0;j<raidPositions.size();j++){
								newBoardState[raidPositions.get(j).get("left")][raidPositions.get(j).get("right")] = currentPlayer;
								newBoardState[row][col] = currentPlayer;
							}
							raidMoves.put("raid " + Integer.toString(row)+" "+ Integer.toString(col), newBoardState);
						}
					}
				}
			}
		}
		return raidMoves;
	}
	public boolean isTerminalState(String[][] boardSt){
		boolean freeSpaceExists = false;
		for(int i= 0; i<sizeOfBoard; i++){
			for(int j = 0; j< sizeOfBoard;j++){
				if(boardSt[i][j].equals(".")){
					freeSpaceExists = true;
					break;
				}
			}
		}
		return freeSpaceExists;
	}
	//**********************************************************************************************//
	//Minimax
	public LinkedHashMap<String, Object> minimaxDecision(String[][] boardState, int d, boolean maximizingPlayer){
		if(d == 0 || !new homework10cases().isTerminalState(boardState)){
			LinkedHashMap<String, Object> best = new LinkedHashMap<String, Object>();
			best.put("bestValue", new homework10cases().calcGameScore(boardState));
			return best;
		}
		if(maximizingPlayer){
			LinkedHashMap<String, Object> best = new LinkedHashMap<String, Object>();
			best.put("bestValue", Double.NEGATIVE_INFINITY);
			LinkedHashMap<String, String[][]> moves = new homework10cases().generateMoves(boardState, maxPlayer);
			Iterator<Entry<String, String[][]>> itMoves = moves.entrySet().iterator();
			while(itMoves.hasNext()) {
				Entry<String, String[][]> move = itMoves.next();
				LinkedHashMap<String, Object> score = new homework10cases().minimaxDecision((String[][]) move.getValue(), d - 1, false);
				if((Double)best.get("bestValue") < (Double)score.get("bestValue")){
					best.put("bestValue", score.get("bestValue"));
					best.put("bestMoveState", move.getValue());
					best.put("bestMove", move.getKey());
				}

			}
			return best;
		}
		else{
			LinkedHashMap<String, Object> best = new LinkedHashMap<String, Object>();
			best.put("bestValue", Double.POSITIVE_INFINITY);
			LinkedHashMap<String, String[][]> moves = new homework10cases().generateMoves(boardState, minPlayer);
			Iterator<Entry<String, String[][]>> itMoves = moves.entrySet().iterator();
			while(itMoves.hasNext()) {
				Entry<String, String[][]> move = itMoves.next();
				LinkedHashMap<String, Object> score = new homework10cases().minimaxDecision((String[][])move.getValue(), d - 1, true);
				if((Double)score.get("bestValue")<(Double) best.get("bestValue")){
					best.put("bestValue", score.get("bestValue"));
					best.put("bestMoveState", move.getValue());
					best.put("bestMove", move.getKey());
				}
			}
			return best;
		}
	}
	//**********************************************************************************************//
	//alphabeta
	public LinkedHashMap<String, Object> alphabetaDecision(String[][] boardState, int d, Double alpha, Double beta, boolean maximizingPlayer){
		if(d == 0 || !new homework10cases().isTerminalState(boardState)){
			LinkedHashMap<String, Object> best = new LinkedHashMap<String, Object>();
			best.put("bestValue", new homework10cases().calcGameScore(boardState));
			return best;
		}
		if(maximizingPlayer){
			LinkedHashMap<String, Object> best = new LinkedHashMap<String, Object>();
			best.put("bestValue", Double.NEGATIVE_INFINITY);
			LinkedHashMap<String, String[][]> moves = new homework10cases().generateMoves(boardState, maxPlayer);
			Iterator<Entry<String, String[][]>> itMoves = moves.entrySet().iterator();
			while(itMoves.hasNext()) {
				Entry<String, String[][]> move = itMoves.next();
				LinkedHashMap<String, Object> score = new homework10cases().alphabetaDecision((String[][]) move.getValue(), d - 1, alpha, beta, false);
				if((Double)best.get("bestValue") < (Double)score.get("bestValue")){
					best.put("bestValue", score.get("bestValue"));
					best.put("bestMoveState", move.getValue());
					best.put("bestMove", move.getKey());
				}
				if (alpha < (Double)best.get("bestValue")){
					alpha =  (Double)best.get("bestValue");
				}
				if (alpha >= beta){
					break;
				}
			}
			return best;
		}
		else{
			LinkedHashMap<String, Object> best = new LinkedHashMap<String, Object>();
			best.put("bestValue", Double.POSITIVE_INFINITY);
			LinkedHashMap<String, String[][]> moves = new homework10cases().generateMoves(boardState, minPlayer);
			Iterator<Entry<String, String[][]>> itMoves = moves.entrySet().iterator();
			while(itMoves.hasNext()) {
				Entry<String, String[][]> move = itMoves.next();
				LinkedHashMap<String, Object> score = new homework10cases().alphabetaDecision((String[][])move.getValue(), d - 1,alpha, beta, true);
				if((Double)score.get("bestValue")<(Double) best.get("bestValue")){
					best.put("bestValue", score.get("bestValue"));
					best.put("bestMoveState", move.getValue());
					best.put("bestMove", move.getKey());
				}
				if ((Double)best.get("bestValue")<beta){
					beta =  (Double)best.get("bestValue");
				}
				if (alpha >= beta){
					break;
				}
			}
			return best;
		}
	}
}