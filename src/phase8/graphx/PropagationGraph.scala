package crisisguard.phase8.graphx

import org.apache.spark._
import org.apache.spark.graphx._
import org.apache.spark.graphx.lib.ShortestPaths
import org.apache.spark.rdd.RDD
import java.io.{File, PrintWriter}

/**
 * CrisisGuard — Phase 8: GraphX Propagation Analytics Engine
 * Author: B.SIVASAI (Roll Number: 2023BCS0228)
 * Course: CSE412 — Big Data & Large-Scale Computing
 * Project: CrisisGuard: A Real-Time Big Data Pipeline for Synthetic Media
 *          Propagation Analysis and Emergency Response Prioritization
 *
 * Implements GraphX analysis on cascade propagation networks:
 * 1. Graph Construction from HDFS vertex & edge datasets
 * 2. In-Degree, Out-Degree, and Total Degree computation
 * 3. Connected Components and Largest Component analysis
 * 4. PageRank structural centrality estimation (20 iterations, resetProb=0.15)
 * 5. Single-Source Shortest Path Reachability from primary cascade seeds
 * 6. Export of structural centrality metrics to HDFS and local feature store
 */
object PropagationGraph {

  def main(args: Array[String]): Unit = {
    println("=" * 70)
    println("CRISISGUARD — PHASE 8 SPARK GRAPHX PROPAGATION ENGINE")
    println("=" * 70)
    println("Author: B.SIVASAI (Roll Number: 2023BCS0228)")
    println("Phase:  8 — Real-Time Propagation Analysis and Graph Intelligence")
    println("=" * 70)

    val startTime = System.currentTimeMillis()

    val conf = new SparkConf()
      .setAppName("CrisisGuard-Phase8-GraphX")
      .setMaster("local[2]")
      .set("spark.driver.memory", "2g")

    val sc = new SparkContext(conf)
    sc.setLogLevel("WARN")

    // Input paths (supports HDFS or local filesystem path passed as args)
    val hdfsVertexPath = if (args.length > 0) args(0) else "hdfs://localhost:9000/crisisguard/phase8/graph/vertices.csv"
    val hdfsEdgePath = if (args.length > 1) args(1) else "hdfs://localhost:9000/crisisguard/phase8/graph/edges.csv"
    val outputDir = if (args.length > 2) args(2) else "data/features/phase8/graph"

    println(s"\n[1] Ingesting Graph Topology:")
    println(s"  - Vertices source: $hdfsVertexPath")
    println(s"  - Edges source:    $hdfsEdgePath")

    // 1. Load Vertices: vertex_id,node_name
    val rawVertices = sc.textFile(hdfsVertexPath)
    val headerV = rawVertices.first()
    val vertices: RDD[(VertexId, String)] = rawVertices
      .filter(line => line != headerV && line.trim.nonEmpty)
      .flatMap { line =>
        val parts = line.split(",")
        if (parts.length >= 2) {
          try {
            Some((parts(0).trim.toLong, parts(1).trim))
          } catch {
            case _: Exception => None
          }
        } else None
      }

    // 2. Load Edges: src_id,dst_id,weight
    val rawEdges = sc.textFile(hdfsEdgePath)
    val headerE = rawEdges.first()
    val edges: RDD[Edge[Double]] = rawEdges
      .filter(line => line != headerE && line.trim.nonEmpty)
      .flatMap { line =>
        val parts = line.split(",")
        if (parts.length >= 2) {
          try {
            val src = parts(0).trim.toLong
            val dst = parts(1).trim.toLong
            val weight = if (parts.length >= 3) parts(2).trim.toDouble else 1.0
            Some(Edge(src, dst, weight))
          } catch {
            case _: Exception => None
          }
        } else None
      }

    // 3. Construct Graph with default vertex attribute
    val defaultUser = "UNKNOWN_NODE"
    val graph: Graph[String, Double] = Graph(vertices, edges, defaultUser)
    graph.cache()

    val numVertices = graph.numVertices
    val numEdges = graph.numEdges

    println(s"\n[2] Graph Construction Complete:")
    println(s"  - Total Vertices: $numVertices")
    println(s"  - Total Directed Edges: $numEdges")

    // 4. Compute Degree Statistics
    println("\n[3] Computing Vertex Degree Distributions...")
    val inDegrees: VertexRDD[Int] = graph.inDegrees
    val outDegrees: VertexRDD[Int] = graph.outDegrees
    val degrees: VertexRDD[Int] = graph.degrees

    val maxInDegree = if (inDegrees.count() > 0) inDegrees.map(_._2).max() else 0
    val maxOutDegree = if (outDegrees.count() > 0) outDegrees.map(_._2).max() else 0
    val maxTotalDegree = if (degrees.count() > 0) degrees.map(_._2).max() else 0

    val meanInDegree = if (numVertices > 0) inDegrees.map(_._2.toDouble).sum() / numVertices else 0.0
    val meanOutDegree = if (numVertices > 0) outDegrees.map(_._2.toDouble).sum() / numVertices else 0.0

    println(s"  - Max In-Degree:    $maxInDegree")
    println(s"  - Max Out-Degree:   $maxOutDegree")
    println(s"  - Max Total Degree: $maxTotalDegree")
    println(f"  - Mean In-Degree:   $meanInDegree%.4f")
    println(f"  - Mean Out-Degree:  $meanOutDegree%.4f")

    // 5. Connected Components Analysis
    println("\n[4] Computing Connected Components...")
    val ccGraph = graph.connectedComponents()
    val ccVertices = ccGraph.vertices
    val componentCounts = ccVertices.map(v => (v._2, 1)).reduceByKey(_ + _)
    val totalComponents = componentCounts.count()
    val largestComponentSize = if (totalComponents > 0) componentCounts.map(_._2).max() else 0

    println(s"  - Total Connected Components: $totalComponents")
    println(s"  - Largest Component Size:     $largestComponentSize vertices")

    // 6. PageRank (20 static iterations, reset probability 0.15)
    println("\n[5] Executing PageRank (20 iterations, damping=0.85)...")
    val prGraph = graph.staticPageRank(20, 0.15)
    val prVertices = prGraph.vertices
    prVertices.cache()

    val maxPageRank = prVertices.map(_._2).max()
    val minPageRank = prVertices.map(_._2).min()
    val meanPageRank = prVertices.map(_._2).sum() / numVertices

    println(f"  - Max PageRank:  $maxPageRank%.6f")
    println(f"  - Min PageRank:  $minPageRank%.6f")
    println(f"  - Mean PageRank: $meanPageRank%.6f")

    // Top 10 structurally central nodes (joined with node names)
    // IMPORTANT: Scientifically termed "structurally central nodes", NOT "confirmed causal sources"
    println("\n[6] Top 10 Structurally Central Nodes (by PageRank):")
    val topCentral = prVertices
      .join(graph.vertices)
      .join(graph.inDegrees)
      .join(graph.outDegrees)
      .map { case (id, (((pr, name), inD), outD)) =>
        (id, name, pr, inD, outD)
      }
      .sortBy(_._3, ascending = false)
      .take(10)

    topCentral.zipWithIndex.foreach { case ((id, name, pr, inD, outD), idx) =>
      println(f"  ${idx + 1}%2d. Vertex $id%5d ($name%12s) | PageRank: $pr%.6f | In-Degree: $inD%3d | Out-Degree: $outD%3d")
    }

    // 7. Shortest Paths (from top central vertex)
    val topSeedId = if (topCentral.nonEmpty) topCentral.head._1 else 1L
    println(s"\n[7] Computing Shortest Path Reachability from Top Central Seed (Vertex $topSeedId)...")
    val spGraph = ShortestPaths.run(graph, Seq(topSeedId))
    val reachableFromSeed = spGraph.vertices.filter { case (_, spMap) => spMap.contains(topSeedId) }
    val reachableCount = reachableFromSeed.count()
    val maxDistance = if (reachableCount > 0) reachableFromSeed.map(_._2(topSeedId)).max() else 0
    println(s"  - Total Vertices Reachable from Seed: $reachableCount")
    println(s"  - Maximum Propagation Depth:          $maxDistance hops")

    // 8. Join All Vertex Metrics and Export
    println(s"\n[8] Exporting Comprehensive GraphX Metrics...")
    val fullMetrics = graph.vertices
      .leftOuterJoin(prVertices)
      .leftOuterJoin(ccVertices)
      .leftOuterJoin(inDegrees)
      .leftOuterJoin(outDegrees)
      .map { case (id, ((((name, prOpt), ccOpt), inDOpt), outDOpt)) =>
        val pr = prOpt.getOrElse(0.0)
        val cc = ccOpt.getOrElse(-1L)
        val inD = inDOpt.getOrElse(0)
        val outD = outDOpt.getOrElse(0)
        (id, name, pr, cc, inD, outD)
      }

    // Write to local CSV
    val localOutFile = new File(s"$outputDir/graphx_vertex_metrics.csv")
    localOutFile.getParentFile.mkdirs()
    val pw = new PrintWriter(localOutFile)
    pw.println("vertex_id,node_name,pagerank,component_id,in_degree,out_degree")
    fullMetrics.collect().foreach { case (id, name, pr, cc, inD, outD) =>
      pw.println(f"$id,$name,$pr%.8f,$cc,$inD,$outD")
    }
    pw.close()
    println(s"  Exported local CSV: ${localOutFile.getPath} ($numVertices vertices)")

    val durationMs = System.currentTimeMillis() - startTime
    val durationSec = durationMs / 1000.0

    // Save summary metrics JSON
    val topNodesJson = topCentral.map { case (id, name, pr, inD, outD) =>
      s"""{"vertex_id": $id, "node_name": "$name", "pagerank": $pr, "in_degree": $inD, "out_degree": $outD}"""
    }.mkString("[", ",", "]")

    val jsonSummary =
      s"""{
         |  "engine": "Apache Spark GraphX",
         |  "scala_version": "2.12.18",
         |  "spark_version": "${sc.version}",
         |  "num_vertices": $numVertices,
         |  "num_edges": $numEdges,
         |  "max_in_degree": $maxInDegree,
         |  "max_out_degree": $maxOutDegree,
         |  "max_total_degree": $maxTotalDegree,
         |  "mean_in_degree": $meanInDegree,
         |  "mean_out_degree": $meanOutDegree,
         |  "total_connected_components": $totalComponents,
         |  "largest_component_size": $largestComponentSize,
         |  "max_pagerank": $maxPageRank,
         |  "min_pagerank": $minPageRank,
         |  "mean_pagerank": $meanPageRank,
         |  "top_seed_vertex_id": $topSeedId,
         |  "seed_reachable_vertices": $reachableCount,
         |  "max_propagation_depth_hops": $maxDistance,
         |  "execution_time_seconds": $durationSec,
         |  "top_structurally_central_nodes": $topNodesJson
         |}""".stripMargin

    val jsonFile = new File("docs/phase8/graphx_metrics_summary.json")
    val jw = new PrintWriter(jsonFile)
    jw.println(jsonSummary)
    jw.close()
    println(s"  Exported metrics JSON: ${jsonFile.getPath}")

    sc.stop()

    println("\n" + "=" * 70)
    println(f"OVERALL GRAPHX STATUS: PASS ($durationSec%.2f seconds execution)")
    println("=" * 70)
  }
}
